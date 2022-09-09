from flask import request
from flask_restx import Resource, Namespace, abort

from project.exceptions import ItemNotFound, ItemAlreadyExists, InvalidToken
from project.container import favourite_service, auth_service, user_service, movie_service
from project.dao.models import FavouriteSchema, MovieSchema

favourite_ns = Namespace('favorites', description='Views for favourites')
favourites_schema = FavouriteSchema(many=True)
favourite_schema = FavouriteSchema()
movies_schema = MovieSchema(many=True)


@favourite_ns.route('/movies/')
class FavouritesViews(Resource):
    @favourite_ns.doc(description='Get user favourites')
    @favourite_ns.response(200, 'Success')
    @favourite_ns.response(404, 'Not found')
    def get(self):
        auth_data = request.headers['Authorization']
        token = auth_data.split("Bearer ")[-1]

        email = auth_service.get_email_from_token(token)
        user_id = user_service.get_by_email(email).id

        favourites = favourite_service.get_user_favourites(user_id)
        return movies_schema.dump(favourites)


@favourite_ns.route('/movies/<int:movie_id>/')
class FavouriteView(Resource):
    @favourite_ns.doc(description='Add favourites', params={'Movie id': 'Movie id'})
    @favourite_ns.response(200, 'Success')
    @favourite_ns.response(404, 'Not found')
    def post(self, movie_id):
        try:
            auth_data = request.headers['Authorization']
            token = auth_data.split("Bearer ")[-1]

            email = auth_service.get_email_from_token(token)
            user_id = user_service.get_by_email(email).id
            movie_check = movie_service.get_one(movie_id)

            favourite_service.add_favourite(user_id, movie_id)
            return "", 200
        except InvalidToken:
            abort(401, "Access denied")
        except ItemAlreadyExists:
            abort(400, 'Favourite already exist')
        except ItemNotFound:
            abort(404, 'Movie not found')

    @favourite_ns.doc(description='Delete favourites', params={'Movie id': 'Movie id'})
    def delete(self, movie_id):
        try:
            auth_data = request.headers['Authorization']
            token = auth_data.split("Bearer ")[-1]

            email = auth_service.get_email_from_token(token)
            user_id = user_service.get_by_email(email).id

            favourite_service.delete_favourite(user_id, movie_id)
            return "", 200
        except InvalidToken:
            abort(401, "Access denied")
        except ItemNotFound:
            abort(404, 'Movie not found in favourites')
