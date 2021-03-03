"""
Models for elastic app
contains models for elastic
Documents -
1. MovieDocument
2. GenreDocument
"""
# Define a default Elastic search client
from elasticsearch_dsl import (
    Document, Object, Text, Keyword,
    Date, Nested, Float, Boolean)
from elasticsearch_dsl.connections import connections

from apps.elastic.constants import MOVIE_INDEX_SHARDS, MOVIE_INDEX_NAME, ES_DOCUMENT_SET
from side_stream import settings

connections.create_connection(hosts=[settings.ELASTIC_HOST])


class MovieDocument(Document):
    """
    Move Document
    """
    id = Text()
    movie_id = Text()
    name = Text(analyzer='snowball', fields={'row': Keyword()}, fielddata=True)
    name_lower = Text(analyzer='snowball', fields={'row': Keyword()}, fielddata=True)
    cover_image = Text()
    cover_image_thumb = Text()
    cover_image_small = Text()
    description = Text()
    is_promoted = Boolean()
    is_deleted = Boolean()
    stream_status = Text()
    status = Text()
    price = Float()

    scheduled_stream = Nested(
        properties={
            'id': Text(),
            'hosting_date': Date(),
            'start_time': Date(),
            'end_time': Date(),
            "user": Object(
                properties={
                    'id': Text(),
                    'full_name': Text(analyzer='snowball', fields={'row': Keyword()}, fielddata=True),
                    'full_name_lower': Text(analyzer='snowball', fields={'row': Keyword()}, fielddata=True),
                    'profile_pic': Text(analyzer='snowball', fields={'row': Keyword()}),
                })

        }
    )

    class Index:
        """
        Index class for MovieDocument
        """
        name = MOVIE_INDEX_NAME
        settings = {
            "number_of_shards": MOVIE_INDEX_SHARDS,
        }


class GenreDocument(Document):
    """
    Genre Document
    """
    genre_id = Text()
    name = Text(analyzer='snowball', fields={'row': Keyword()}, fielddata=True)
    name_lower = Text(analyzer='snowball', fields={'row': Keyword()}, fielddata=True)
    picture = Text()
    is_active = Boolean()
    is_deleted = Boolean()
    is_picture_deleted = Boolean()
    genre_movies = Nested(
        properties={
            'id': Text(),
            'movie__id': Text(),
            'movie__name': Text(),
        }
    )

    class Index:
        """
        Index class for MovieDocument
        """
        name = ES_DOCUMENT_SET['genre']
        settings = {
            "number_of_shards": ES_DOCUMENT_SET['genre_index_shared'],
        }


def initialize_document():
    """
    Initialize stream/movie documents.
    :return:
    """
    MovieDocument.init()
    GenreDocument.init()
