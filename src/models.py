from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(80), unique=False, nullable=False)
    is_active = db.Column(db.Boolean(), unique=False, nullable=False)
    favorites = db.relationship('Favorite', back_populates='user', lazy=True)

    def __repr__(self):
        return '<User %r>' % self.email

    def serialize(self):
        return {
            "id": self.id,
            "email": self.email,
        }


class Planet(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    population = db.Column(db.BigInteger, nullable=True)
    terrain = db.Column(db.String(120), nullable=True)
    climate = db.Column(db.String(120), nullable=True)

    favorite_planets = db.relationship(
        'Favorite', back_populates='planet_rel', lazy=True)

    def __repr__(self):
        return '<Planet %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "population": self.population,
            "terrain": self.terrain,
            "climate": self.climate
        }


class People(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), unique=True, nullable=False)
    height = db.Column(db.Integer, nullable=True)
    mass = db.Column(db.Integer, nullable=True)
    hair_color = db.Column(db.String(50), nullable=True)
    skin_color = db.Column(db.String(50), nullable=True)
    eye_color = db.Column(db.String(50), nullable=True)
    birth_year = db.Column(db.String(50), nullable=True)
    gender = db.Column(db.String(50), nullable=True)

    favorite_people = db.relationship(
        'Favorite', back_populates='person_rel', lazy=True)

    def __repr__(self):
        return '<People %r>' % self.name

    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "height": self.height,
            "mass": self.mass,
            "hair_color": self.hair_color,
            "skin_color": self.skin_color,
            "eye_color": self.eye_color,
            "birth_year": self.birth_year,
            "gender": self.gender
        }


class Favorite(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', back_populates='favorites')
    planet_id = db.Column(
        db.Integer, db.ForeignKey('planet.id'), nullable=True)
    people_id = db.Column(
        db.Integer, db.ForeignKey('people.id'), nullable=True)

    planet_rel = db.relationship('Planet', back_populates='favorite_planets')
    person_rel = db.relationship('People', back_populates='favorite_people')

    def __repr__(self):
        return f'<Favorite user_id: {self.user_id}, planet_id: {self.planet_id}, people_id: {self.people_id}>'

    def serialize(self):
        data = {
            "id": self.id,
            "user_id": self.user_id,
        }
        if self.planet_id:
            data["planet"] = self.planet_rel.serialize(
            ) if self.planet_rel else None
            data["planet_id"] = self.planet_id
        if self.people_id:
            data["person"] = self.person_rel.serialize(
            ) if self.person_rel else None
            data["people_id"] = self.people_id
        return data
