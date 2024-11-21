import os
from BookingSystem import db, login_manager
from flask_login import UserMixin
from flask import url_for
from flask_mail import Message
from BookingSystem import mail, bcrypt
from flask import current_app 
from . import db 
from itsdangerous import URLSafeTimedSerializer as Serializer
from datetime import datetime
from enum import Enum



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(db.Model, UserMixin):
    __tablename__ = 'Users'
    __table_args__ = (  
        db.Index('idx_users_email', 'email'),
        db.Index('idx_users_role', 'role'),
        # {'schema': 'public'},
    )
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(15), nullable=False)  # admin, tour operator, tour guide
    last_name = db.Column(db.String(50))
    first_name = db.Column(db.String(50))
    profile_img = db.Column(db.String(225), default='default.jpg')
    nationality = db.Column(db.String(100))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    confirmed = db.Column(db.Boolean, default=False)
    tour = db.Column(db.Integer)

    # Relationships
    tour_operator = db.relationship('TourOperator',backref='user',uselist=False,cascade="all, delete-orphan")
    tour_guide = db.relationship('TourGuide',backref='user',uselist=False,cascade="all, delete-orphan")
    reviews = db.relationship('ReviewsRating',backref='user', cascade="all, delete-orphan")
    bookings = db.relationship('Booking',backref='user',cascade="all, delete-orphan")
    
    
    # @property
    # def is_active(self):
    #     return self.active  # Ensure there's an 'active' field in the User model

    @property
    def is_authenticated(self):
        return True  # This is always true for a logged-in user

    @property
    def is_anonymous(self):
        return False  # This is always false for a logged-in user
    
    @property
    def is_tourguide(self):
        return self.role == 'tourguide'

    def get_id(self):
        return self.id  # Return the unique identifier for the user

    def set_password(self, password):
        self.password = bcrypt.generate_password_hash(password).decode('utf-8')

    def check_password(self, password):
        return bcrypt.check_password_hash(self.password, password)

    def get_reset_token(self, expires_sec=3600):
        """Generate a reset token that expires in expires_sec seconds."""
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})
    
    def __repr__(self):
        return f"<User '{self.email}', '{self.profile_img}'>"
    

    
    @staticmethod
    def verify_reset_token(token, expires_sec=3600):
        """Verify the reset token and return the user if valid."""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, max_age=expires_sec)['user_id']
        except Exception as e:
            print(f"Error loading token: {e}")  # Debugging output
            return None
        return User.query.get(user_id)

    def send_reset_email(self):
        token = self.get_reset_token()
        msg = Message('Password Reset Request', 
                    sender=os.environ.get('MAIL_DEFAULT_SENDER'), 
                    recipients=[self.email])
        msg.body = f'''To reset your password, visit the following link:
        {url_for('main.traveler_reset_token', token=token, _external=True)}

        If you did not make this request, simply ignore this email and no changes will be made.
        '''
        print(f"Message created: {msg}")  # Debugging output
        mail.send(msg)

    def get_confirmation_token(self, expires_sec=3600):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id}, salt='email-confirm')

    @staticmethod
    def verify_confirmation_token(token, expires_sec=3600):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, salt='email-confirm', max_age=expires_sec)['user_id']
        except Exception as e:
            print(f"Error loading token: {e}")  # Debugging output
            return None
        return User.query.get(user_id)

def send_confirmation_email(self):
    token = self.get_confirmation_token()
    msg = Message('Confirm Your Email', recipients=[self.email])
    msg.body = f'''To confirm your email, visit the following link:
    {url_for('main.confirm_email', token=token, _external=True)}
    '''
    mail.send(msg)
    
class TourOperator(db.Model, UserMixin):
    __tablename__ = 'Tour_Operator'
    __table_args__ = ( 
        db.Index('idx_tour_operator_user_id', 'user_id'),  # Index on user_id
        # {'schema': 'public'},
    )
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id', ondelete='CASCADE'),unique=True, nullable=False)
    municipal = db.Column(db.String(100))
    contact_num = db.Column(db.String(15))

    # Relationships
    tour_guides = db.relationship('TourGuide', backref='tour_operator', cascade="all, delete-orphan")
    
    @staticmethod
    def verify_reset_token(token, expires_sec=3600):
        """Verify the reset token and return the user if valid."""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, max_age=expires_sec)['user_id']
        except Exception as e:
            print(f"Error loading token: {e}")  # Debugging output
            return None
        return User.query.get(user_id)

    def send_reset_email(self):
        token = self.get_reset_token()
        msg = Message('Password Reset Request', 
                    sender=os.environ.get('MAIL_DEFAULT_SENDER'), 
                    recipients=[self.email])
        msg.body = f'''To reset your password, visit the following link:
        {url_for('main.traveler_reset_token', token=token, _external=True)}

        If you did not make this request, simply ignore this email and no changes will be made.
        '''
        print(f"Message created: {msg}")  # Debugging output
        mail.send(msg)

    def get_confirmation_token(self, expires_sec=3600):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id}, salt='email-confirm')

    @staticmethod
    def verify_confirmation_token(token, expires_sec=3600):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, salt='email-confirm', max_age=expires_sec)['user_id']
        except Exception as e:
            print(f"Error loading token: {e}")  # Debugging output
            return None
        return User.query.get(user_id)

def send_confirmation_email(self):
    token = self.get_confirmation_token()
    msg = Message('Confirm Your Email', recipients=[self.email])
    msg.body = f'''To confirm your email, visit the following link:
    {url_for('main.confirm_email', token=token, _external=True)}
    '''
    mail.send(msg)


class TourGuide(db.Model, UserMixin):
    __tablename__ = 'Tour_Guide'
    __table_args__ = (
        db.Index('idx_tour_guide_user_id', 'user_id'),        # Index on user_id
        db.Index('idx_tour_guide_toperator_id', 'toperator_id'), # Index on toperator_id
        db.Index('idx_tour_guide_active', 'active'),          # Index on active
        # {'schema': 'public'},
    )
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer,db.ForeignKey('Users.id', ondelete='CASCADE'), unique=True,nullable=False)
    toperator_id = db.Column(db.Integer,db.ForeignKey('Tour_Operator.id', ondelete='CASCADE'), nullable=False)
    accredited_num = db.Column(db.String(50))
    bio = db.Column(db.Text)
    price = db.Column(db.Numeric(10, 2), default=1200)
    specialization = db.Column(db.String(255))
    contact_num = db.Column(db.String(15))
    active = db.Column(db.Boolean, default=False)
    
    # Relationships
    characteristics = db.relationship('Characteristic', backref='tour_guide', cascade="all, delete-orphan")
    skills = db.relationship('Skill', backref='tour_guide', cascade="all, delete-orphan")
    availability = db.relationship('Availability', backref='tour_guide', cascade="all, delete-orphan")
    reviews = db.relationship('ReviewsRating', backref='tour_guide', cascade="all, delete-orphan")
    bookings = db.relationship('Booking', backref='tour_guide', cascade="all, delete-orphan")
    notifications = db.relationship('Notification', backref='tour_guide', cascade="all, delete-orphan")
    
    @staticmethod
    def verify_reset_token(token, expires_sec=3600):
        """Verify the reset token and return the user if valid."""
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, max_age=expires_sec)['user_id']
        except Exception as e:
            print(f"Error loading token: {e}")  # Debugging output
            return None
        return User.query.get(user_id)

    def send_reset_email(self):
        token = self.get_reset_token()
        msg = Message('Password Reset Request', 
                    sender=os.environ.get('MAIL_DEFAULT_SENDER'), 
                    recipients=[self.email])
        msg.body = f'''To reset your password, visit the following link:
        {url_for('main.traveler_reset_token', token=token, _external=True)}

        If you did not make this request, simply ignore this email and no changes will be made.
        '''
        print(f"Message created: {msg}")  # Debugging output
        mail.send(msg)

    def get_confirmation_token(self, expires_sec=3600):
        s = Serializer(current_app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id}, salt='email-confirm')

    @staticmethod
    def verify_confirmation_token(token, expires_sec=3600):
        s = Serializer(current_app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token, salt='email-confirm', max_age=expires_sec)['user_id']
        except Exception as e:
            print(f"Error loading token: {e}")  # Debugging output
            return None
        return User.query.get(user_id)

def send_confirmation_email(self):
    token = self.get_confirmation_token()
    msg = Message('Confirm Your Email', recipients=[self.email])
    msg.body = f'''To confirm your email, visit the following link:
    {url_for('main.confirm_email', token=token, _external=True)}
    '''
    mail.send(msg)


class Characteristic(db.Model):
    __tablename__ = 'Characteristic'
    __table_args__ = (
        db.Index('idx_characteristic_tguide_id', 'tguide_id'),  # Index on tguide_id
        # {'schema': 'public'},
    )
    id = db.Column(db.Integer, primary_key=True)
    tguide_id = db.Column(db.Integer, db.ForeignKey('Tour_Guide.id'), nullable=False)
    characteristic = db.Column(db.String(100))


class Skill(db.Model):
    __tablename__ = 'Skill'
    __table_args__ = ( 
        db.Index('idx_skill_tguide_id', 'tguide_id'),  # Index on tguide_id
        # {'schema': 'public'},
    )
    id = db.Column(db.Integer, primary_key=True)
    tguide_id = db.Column(db.Integer, db.ForeignKey('Tour_Guide.id'), nullable=False)
    skill = db.Column(db.String(100))


class AvailabilityStatus(Enum):
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    BOOKED = "booked"

class Availability(db.Model):
    __tablename__ = 'Availability'
    __table_args__ = (
        db.Index('idx_availability_tguide_id', 'tguide_id'),
        db.Index('idx_availability_date', 'availability_date'),
    )

    id = db.Column(db.Integer, primary_key=True)
    tguide_id = db.Column(db.Integer, db.ForeignKey('Tour_Guide.id'), nullable=False)
    availability_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(20), nullable=False, default=AvailabilityStatus.AVAILABLE.value)

    # Optional method to convert enum to string for consistency
    def set_status(self, status: AvailabilityStatus):
        self.status = status.value


class TourPackage(db.Model):
    __tablename__ = 'TourPackage'
    __table_args__ = (
        db.Index('idx_tour_package_name', 'name'),
        db.Index('idx_tour_package', 'toperator_id'), # Index on toperator_id
    )
    id = db.Column(db.Integer, primary_key=True)
    toperator_id = db.Column(db.Integer, db.ForeignKey('Tour_Operator.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    description = db.Column(db.Text)
    package_img = db.Column(db.String(255))

    # Relationships
    estimated_prices = db.relationship('EstimatedPrice', backref='tour_package', cascade="all, delete-orphan")
    inclusions = db.relationship('Inclusion', backref='tour_package', cascade="all, delete-orphan")
    exclusions = db.relationship('Exclusion', backref='tour_package', cascade="all, delete-orphan")
    itineraries = db.relationship('Itinerary', backref='tour_package', cascade="all, delete-orphan")


class EstimatedPrice(db.Model):
    __tablename__ = 'Estimated_Price'
    __table_args__ = (
        db.Index('idx_estimated_price_package_id', 'package_id'),
    )
    id = db.Column(db.Integer, primary_key=True)
    package_id = db.Column(db.Integer, db.ForeignKey('TourPackage.id', ondelete="CASCADE"), nullable=False)
    description = db.Column(db.String(100))
    estimated_price = db.Column(db.Numeric(10, 2))


class Inclusion(db.Model):
    __tablename__ = 'Inclusion'
    __table_args__ = (
    db.Index('idx_inclusion_package_id', 'package_id'),
    )
    id = db.Column(db.Integer, primary_key=True)
    package_id = db.Column(db.Integer, db.ForeignKey('TourPackage.id', ondelete="CASCADE"), nullable=False)
    inclusion = db.Column(db.String(100))


class Exclusion(db.Model):
    __tablename__ = 'Exclusion'
    __table_args__ = (
        db.Index('idx_exclusion_package_id', 'package_id'),
    )
    id = db.Column(db.Integer, primary_key=True)
    package_id = db.Column(db.Integer, db.ForeignKey('TourPackage.id', ondelete="CASCADE"), nullable=False)
    exclusion = db.Column(db.String(100))


class Itinerary(db.Model):
    __tablename__ = 'Itinerary'
    __table_args__ = (
        db.Index('idx_itinerary_package_id', 'package_id'),
    )
    id = db.Column(db.Integer, primary_key=True)
    package_id = db.Column(db.Integer, db.ForeignKey('TourPackage.id', ondelete="CASCADE"), nullable=False)
    title = db.Column(db.String(100))
    subtitle = db.Column(db.String(100))

class Booking(db.Model):
    __tablename__ = 'Booking'
    __table_args__ = (
        db.Index('idx_booking_user_id', 'user_id'),               # Index on user_id
        db.Index('idx_booking_tour_guide_id', 'tour_guide_id'),   # Index on tour_guide_id
        db.Index('idx_booking_package_id', 'package_id'),         # Index on package_id
        db.Index('idx_booking_status', 'status'),                 # Index on status
        db.Index('idx_booking_date_start', 'date_start'),         # Index on date_start
        # {'schema': 'public'},
    )
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=True)
    tour_guide_id = db.Column(db.Integer, db.ForeignKey('Tour_Guide.id'), nullable=False)
    package_id = db.Column(db.Integer, db.ForeignKey('TourPackage.id'), nullable=False)
    status = db.Column(db.String(15), nullable=False)
    date_start = db.Column(db.Date)
    date_end = db.Column(db.Date)
    traveler_quantity = db.Column(db.Integer, nullable=False)
    special_notes = db.Column(db.Text)
    time = db.Column(db.Time, nullable=False)
    duration = db.Column(db.Interval)
    price = db.Column(db.Numeric(10, 2))
    
class Notification(db.Model):
    __tablename__ = 'Notification'
    __table_args__ = (
        db.Index('idx_notification_tguide_id', 'tguide_id'),   # Index on tguide_id
        db.Index('idx_notification_booking_id', 'booking_id'), # Index on booking_id
        db.Index('idx_notification_is_read', 'is_read'),       # Index on is_read
        # {'schema': 'public'},
    )
    id = db.Column(db.Integer, primary_key=True)
    tguide_id = db.Column(db.Integer, db.ForeignKey('Tour_Guide.id'), nullable=False)
    booking_id = db.Column(db.Integer, db.ForeignKey('Booking.id', ondelete="CASCADE"), nullable=False)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ReviewsRating(db.Model):
    __tablename__ = 'Reviews_Rating'
    __table_args__ = (
        db.Index('idx_reviews_rating_user_id', 'user_id'),           # Index on user_id
        db.Index('idx_reviews_rating_tour_guide_id', 'tour_guide_id'), # Index on tour_guide_id
        db.Index('idx_reviews_rating_rating', 'rating'),             # Index on rating
        # {'schema': 'public'},
    )
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('Users.id'), nullable=True)
    tour_guide_id = db.Column(db.Integer, db.ForeignKey('Tour_Guide.id', ondelete="CASCADE"), nullable=False)
    rating = db.Column(db.Numeric(2, 1))
    comment = db.Column(db.Text)
    datetime = db.Column(db.DateTime, default=datetime.utcnow)


class ReviewImages(db.Model):
    __tablename__ = 'Review_Images'
    __table_args__ = (
        db.Index('idx_review_images_rr_id', 'rr_id'),  # Index on rr_id
        # {'schema': 'public'},
    )
    id = db.Column(db.Integer, primary_key=True)
    rr_id = db.Column(db.Integer, db.ForeignKey('Reviews_Rating.id', ondelete="CASCADE"), nullable=False)
    img = db.Column(db.String(255))



    
    
    
