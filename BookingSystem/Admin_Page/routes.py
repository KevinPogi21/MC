from flask import render_template, redirect, url_for, flash, session
from flask_login import login_required, current_user, logout_user
from . import admin
from werkzeug.security import generate_password_hash
from BookingSystem import db, bcrypt
from BookingSystem.Admin_Page.forms import UserTourOperatorForm
from BookingSystem.models import User, TourOperator, send_confirmation_email, TourGuide
from flask import request
from sqlalchemy.orm import aliased

# Create Tour Operator
@admin.route('/create_operator', methods=['GET', 'POST'])
@login_required
def create_operator():
    form = UserTourOperatorForm()  # Instantiate the form
    if form.validate_on_submit():
        # Hash the password from the form
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        
        # Create a new UserTourOperator instance
        new_user = User(
            first_name=form.name.data,
            email=form.email.data,
            password=hashed_password,
            role='touroperator',  # Set role as tour operator
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            
            # Create a TourOperator entry linked to the new user
            new_operator = TourOperator(
                user_id=new_user.id,
                contact_num=form.contact_number.data,
                municipal=form.municipal.data,
            )
            db.session.add(new_operator)
            db.session.commit()
            send_confirmation_email(new_user)

            flash('Tour Operator account created successfully!', 'success')
            return redirect(url_for('main.pending_confirmation', operator_id=new_user.id))  # Redirect to the tour operator profile
        except Exception as e:
            db.session.rollback()  # Rollback if there's an error
            # flash('An error occurred while creating the account. Please try again.', 'danger')
            print(f"Database error: {e}")  # For debugging, remove in production

    return render_template('admin_dashboard.html', form=form)  # Render the admin dashboard template

# @admin.route('/tour_operator_profile/<int:operator_id>', methods=['GET'])
# @login_required
# def tour_operator_profile(operator_id):
#     # Fetch the user and tour operator details based on operator_id
#     operator = User.query.get_or_404(operator_id)
#     tour_operator = TourOperator.query.filter_by(user_id=operator_id).first_or_404()

#     return render_template('touroperator_dashboard.html',form=form, operator=operator, tour_operator=tour_operator)








@admin.route('/dashboard')
@login_required
def admin_dashboard():
    if current_user.role != 'admin':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.home'))  # Redirect to the main home page

    form = UserTourOperatorForm()  # Create an instance of the OperatorForm
    tour_operators = TourOperator.query.all()
    role_filter = request.args.get('role', '')  # Default is no filter

    if role_filter == 'tourguide':
        # Create alias for the Users table to represent the Tour Operator
        operator_user = aliased(User)
        # Join TourGuide, User (for tour guide info), and User (for tour operator info)
        users = db.session.query(
            User.last_name.label('guide_last_name'),
            User.first_name.label('guide_first_name'),
            User.email,
            TourGuide.active,
            operator_user.first_name.label('operator_first_name')
        ).join(
            TourGuide, User.id == TourGuide.user_id
        ).join(
            TourOperator, TourGuide.toperator_id == TourOperator.id
        ).join(
            operator_user, TourOperator.user_id == operator_user.id  # Join with the aliased User for the operator
        ).filter(
            User.role == 'tourguide'  # Ensure we are filtering for 'tour guide'
        ).all()

    elif role_filter == 'touroperator':
        # Fetch tour operators with municipal information
        users = db.session.query(User, TourOperator.municipal).join(
            TourOperator, User.id == TourOperator.user_id
        ).filter(User.role == 'touroperator').all()

    elif role_filter and role_filter in ['traveler']:
        users = User.query.filter(User.role == role_filter).all()
    else:
        users = User.query.filter(User.role != 'admin').all()

    return render_template('admin_dashboard.html', title='Admin Dashboard', form=form, tour_operators=tour_operators, users=users, role_filter=role_filter)  # Render the dashboard with the form

@admin.route('/logout')
@login_required  # Ensure user is logged in before logging out
def logout():
    logout_user()
    session.pop('user_id', None) 
    flash('You have been logged out.', 'info')  # Optional: Notify user
    return redirect(url_for('main.home'))
