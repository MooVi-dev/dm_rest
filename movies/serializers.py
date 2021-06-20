from rest_framework import serializers

from .models import Movie, Review, Rating, Actor


class RecursiveSerializer(serializers.Serializer):
    """Вывод рекурсивно детей"""
    def to_representation(self, value):
        serializer = self.parent.parent.__class__(value, context=self.context)
        # Берет экземпляр сериализатора parent, который есть ListSerializer
        # (он появился из-за того, что мы передали many = True в RecursiveSerializer).
        # После этого он берет parent экземпляр нашего parent'а
        # и достает ссылку на его класс
        return serializer.data


class MovieListSerializer(serializers.ModelSerializer):
    """Список фильмов"""
    rating_user = serializers.BooleanField()
    middle_star = serializers.IntegerField()

    class Meta:
        model = Movie
        fields = ('id', 'title', 'tagline', 'category', 'rating_user', 'middle_star')


class MovieCreateSerializer(serializers.ModelSerializer):
    """Добавление описания фильма"""

    class Meta:
        model = Movie
        fields = ('__all__')


class ActorListSerializer(serializers.ModelSerializer):
    """Список актеров и режиссеров"""

    class Meta:
        model = Actor
        fields = ('id', 'name', 'image')


class ActorDetailSerializer(serializers.ModelSerializer):
    """Вывод информации об актерах и режиссерах"""

    class Meta:
        model = Actor
        fields = ('__all__')


class ReviewCreateSerializer(serializers.ModelSerializer):
    """Добавление отзыва к фильму"""

    class Meta:
        model = Review
        fields = '__all__'


class ReviewSerializer(serializers.ModelSerializer):
    """Вывод отзыва"""
    children = RecursiveSerializer(many=True)

    class Meta:
        model = Review
        fields = ('name', 'text', 'children')


class MovieDetailSerializer(serializers.ModelSerializer):
    """Полное описание фильма"""
    category = serializers.SlugRelatedField(slug_field='name', read_only=True)
    directors = ActorListSerializer(read_only=True, many=True)
    actors = ActorDetailSerializer(read_only=True, many=True)
    genres = serializers.SlugRelatedField(slug_field='name', read_only=True, many=True)
    reviews = ReviewSerializer(many=True)

    class Meta:
        model = Movie
        exclude = ('draft',)


class CreateRatingSerializer(serializers.ModelSerializer):
    """Добавление рейтинга пользователем"""
    class Meta:
        model = Rating
        fields = ('star', 'movie')

    def create(self, validation_data):
        rating, _ = Rating.objects.update_or_create(
            ip=validation_data.get('ip', None),
            movie=validation_data.get('movie', None),
            defaults={'star': validation_data.get('star')}
        )
        return rating

