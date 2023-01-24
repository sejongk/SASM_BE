import io
import time

from django.conf import settings
from django.db import transaction
from django.core.files.images import ImageFile
from django.core.files.uploadedfile import UploadedFile, InMemoryUploadedFile
from django.core.exceptions import ValidationError as DjangoValidationError

from rest_framework import exceptions

from users.models import User
from community.models import Board, Post, PostHashtag, PostPhoto, PostLike
from .selectors import BoardSelector, PostHashtagSelector, PostSelector, PostLikeSelector


class PostCoordinatorService:
    def __init__(self, user: User):
        self.user = user

    @transaction.atomic
    def create(self, board_id: int, title: str, content: str, hashtag_names: list[str] = None, image_files: list[InMemoryUploadedFile] = None) -> Post:
        board = BoardSelector.get_from_id(id=board_id)

        post_service = PostService()
        post = post_service.create(
            title=title,
            content=content,
            board=board,
            writer=self.user
        )

        if board.supports_hashtags and hashtag_names:
            hashtag_service = PostHashtagService(post=post)
            hashtag_service.create(names=hashtag_names)

        # [TODO] 문제점: tx가 중간에 실패할 경우, S3에 저장된 image는 삭제되지 않아 orphan 이미지 존재
        # 아래 링크처럼 예외 처리에서 boto3를 이용해 수동 삭제 or CRON을 이용해 주기적으로 orphan 정리
        # ref. https://stackoverflow.com/questions/50222974/django-transactions-how-to-run-extra-code-during-rollback
        if board.supports_post_photos and image_files:
            photo_service = PostPhotoService(post=post)
            photo_service.create(image_files=image_files)

        return post

    @transaction.atomic
    def update(self, post_id: int, title: str, content: str, hashtag_names: list[str] = [], photo_image_urls: list[str] = [], image_files: list[InMemoryUploadedFile] = []) -> Post:
        post_service = PostService()
        post_selector = PostSelector()

        # user가 해당 post의 writer가 아닐 경우 에러 raise
        if not post_selector.isWriter(post_id=post_id, user=self.user):
            raise exceptions.ValidationError({"error": "게시글 작성자가 아닙니다."})

        post = post_service.update(
            post_id=post_id,
            title=title,
            content=content,
        )

        if post.board.supports_hashtags:
            hashtag_service = PostHashtagService(post=post)
            hashtag_service.update(names=hashtag_names)

        if post.board.supports_post_photos:
            photo_service = PostPhotoService(post=post)
            photo_service.update(
                photo_image_urls=photo_image_urls,
                image_files=image_files
            )

        return post

    @transaction.atomic
    def delete(self, post_id: int):
        post_service = PostService()
        post_selector = PostSelector()

        # user가 해당 post의 writer가 아닐 경우 에러 raise
        if not post_selector.isWriter(post_id=post_id, user=self.user):
            raise exceptions.ValidationError({"error": "게시글 작성자가 아닙니다."})

        post_service.delete(post_id=post_id)

    @transaction.atomic
    def like_or_dislike(self, post_id: int) -> bool:
        # 이미 좋아요 한 상태 -> 좋아요 취소 (dislike)
        if PostLikeSelector.likes(post_id=post_id, user=self.user):
            # PostLike 삭제
            PostLikeService.dislike(
                post_id=post_id,
                user=self.user
            )

            # Post의 like_cnt 1 감소
            PostService.dislike(post_id=post_id)
            return False

        else:  # 좋아요 하지 않은 상태 -> 좋아요 (like)
            # PostLike 생성
            PostLikeService.like(
                post_id=post_id,
                user=self.user
            )

            # Post의 like_cnt 1 증가
            PostService.like(post_id=post_id)
            return True


class PostService:
    def __init__(self):
        pass

    def create(self, title: str, content: str, board: Board, writer: User) -> Post:
        post = Post(
            title=title,
            content=content,
            board=board,
            writer=writer
        )

        post.full_clean()
        post.save()

        return post

    def update(self, post_id: int, title: str, content: str) -> Post:
        post = Post.objects.get(id=post_id)

        post.update_title(title)
        post.update_content(content)

        post.full_clean()
        post.save()

        return post

    def delete(self, post_id: int):
        post = Post.objects.get(id=post_id)

        post.delete()

    @staticmethod
    def like(post_id: int):
        post = Post.objects.get(id=post_id)

        post.like()

        post.full_clean()
        post.save()

    @staticmethod
    def dislike(post_id: int):
        post = Post.objects.get(id=post_id)

        post.dislike()

        post.full_clean()
        post.save()


class PostHashtagService:
    def __init__(self, post: Post):
        self.post = post

    def create(self, names: list[str]):
        hashtags = []

        # 중복된 이름을 가진 해시태그 제거를 위해 set 자료구조 사용
        names = set(names)

        for name in names:
            hashtag = PostHashtag(
                name=name,
                post=self.post
            )

            hashtag.full_clean()
            hashtag.save()

            hashtags.append(hashtag)

        return hashtags

    def update(self, names: list[str]):
        hashtags = []

        current_hashtags = self.post.hashtags.all()

        # names에 포함되지 않은 해시태그 삭제
        for current_hashtag in current_hashtags:
            if current_hashtag.name not in names:
                current_hashtag.delete()
            else:
                hashtags.append(current_hashtag)

        # 신규 name을 해시태그 생성
        selector = PostHashtagSelector()
        for name in names:
            # 이미 존재하는 해시태그면 스킵
            if selector.exists(post=self.post, name=name):
                continue
            # 존재하지 않으면 생성
            hashtag = PostHashtag(
                name=name,
                post=self.post
            )
            hashtag.full_clean()
            hashtag.save()

            hashtags.append(hashtag)

        return hashtags


class PostPhotoService:
    def __init__(self, post: Post):
        self.post = post

    def create(self, image_files: list[InMemoryUploadedFile]) -> PostPhoto:
        photos = []

        for image_file in image_files:
            ext = image_file.name.split(".")[-1]
            file_path = '{}-{}.{}'.format(self.post.id,
                                          str(int(time.time())), ext)
            image = ImageFile(io.BytesIO(image_file.read()), name=file_path)

            photo = PostPhoto(
                image=image,
                post=self.post
            )

            photo.full_clean()
            photo.save()

            photos.append(photo)

        return photos

    def update(self, photo_image_urls: list[str], image_files: list[InMemoryUploadedFile]):
        photos = []

        current_photos = self.post.photos.all()

        # photo_image_urls에 포함되지 않은 이미지를 가진 photo 삭제
        for current_photo in current_photos:
            image_path = settings.MEDIA_URL + str(current_photo.image)
            if image_path not in photo_image_urls:
                current_photo.delete()
            else:
                photos.append(current_photo)

        # 신규 image_file을 photo로 생성
        photos.extend(self.create(image_files=image_files))

        return photos


class PostLikeService:
    def __init__(self):
        pass

    @staticmethod
    def like(post_id: int, user: User):
        like = PostLike(
            post=Post.objects.get(id=post_id),
            user=user
        )
        like.full_clean()
        like.save()

    @staticmethod
    def dislike(post_id: int, user: User):
        PostLike.objects.get(post__id=post_id, user=user).delete()