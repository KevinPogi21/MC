from flask import render_template, redirect, url_for, flash, request, session, jsonify,current_app
from flask_login import login_required, current_user, logout_user
from . import touroperator  
from werkzeug.security import generate_password_hash, check_password_hash
from BookingSystem import bcrypt, db 
from BookingSystem.TourOperator_Page.form import UserTourGuideForm,TourPackageForm
from BookingSystem.models import User, TourOperator, TourGuide , send_confirmation_email, TourPackage, EstimatedPrice, Inclusion, Exclusion, Itinerary
from werkzeug.utils import secure_filename
import os
from flask import jsonify
from BookingSystem.models import ReviewsRating, ReviewImages


@touroperator.route('/create_tour_package', methods=['GET', 'POST'])
@login_required
def create_tour_package():
    package_form = TourPackageForm()
    guide_form = UserTourGuideForm()  # Instantiate the form for the dashboard
    tour_guides = TourGuide.query.filter_by(toperator_id=current_user.tour_operator.id).all()
    operator = TourOperator.query.filter_by(user_id=current_user.id).first()
    packages = TourPackage.query.filter_by(toperator_id=current_user.tour_operator.id).all()

    # Define the specific upload folder for package images
    package_upload_folder = os.path.join(current_app.root_path, 'static/package_pics')
    os.makedirs(package_upload_folder, exist_ok=True)  # Ensure the folder exists

    if package_form.validate_on_submit():
        # Handle file upload
        file = package_form.package_img.data  # Access the uploaded file
        filename = None

        if file:
            # Secure the filename to avoid path injection
            filename = secure_filename(file.filename)
            # Save the file to the specific upload folder
            file_path = os.path.join(package_upload_folder, filename)
            file.save(file_path)

        # Create the main TourPackage instance
        tour_package = TourPackage(
            toperator_id=current_user.tour_operator.id,
            name=package_form.name.data,
            description=package_form.description.data,
            package_img=f"package_pics/{filename}"  # Store relative path
        )
        db.session.add(tour_package)
        db.session.flush()  # Flush to get the tour_package ID
        
        # Process Estimated Price entries
        estimated_price_descriptions = request.form.getlist('estimated_price_description[]')
        estimated_price_values = request.form.getlist('estimated_price_value[]')
        for desc, price in zip(estimated_price_descriptions, estimated_price_values):
            if desc and price:  # Validate presence
                estimated_price = EstimatedPrice(
                    package_id=tour_package.id,
                    description=desc,
                    estimated_price=price
                )
                db.session.add(estimated_price)

        # Process Inclusions
        inclusions = request.form.getlist('inclusions[]')
        for inclusion_text in inclusions:
            if inclusion_text:
                inclusion = Inclusion(
                    package_id=tour_package.id,
                    inclusion=inclusion_text
                )
                db.session.add(inclusion)

        # Process Exclusions
        exclusions = request.form.getlist('exclusions[]')
        for exclusion_text in exclusions:
            if exclusion_text:
                exclusion = Exclusion(
                    package_id=tour_package.id,
                    exclusion=exclusion_text
                )
                db.session.add(exclusion)

        # Process Itinerary
        itinerary_titles = request.form.getlist('itinerary_title[]')
        itinerary_subtitles = request.form.getlist('itinerary_subtitle[]')
        for title, subtitle in zip(itinerary_titles, itinerary_subtitles):
            if title and subtitle:
                itinerary = Itinerary(
                    package_id=tour_package.id,
                    title=title,
                    subtitle=subtitle
                )
                db.session.add(itinerary)

        db.session.commit()  # Commit all changes
        flash("Tour package created successfully!", "success")
        return redirect(url_for('touroperator.touroperator_dashboard'))

    # Render the tour operator dashboard with the form
    return render_template('touroperator_dashboard.html', guide_form=guide_form, package_form=package_form,
                           tour_guides=tour_guides, operator=operator, packages=packages)
    

@touroperator.route('/get_tour_package/<int:package_id>', methods=['GET'])
@login_required
def get_tour_package(package_id):
    package = TourPackage.query.get_or_404(package_id)

    # Format the data for JSON response
    package_data = {
        "name": package.name,
        "description": package.description,
        "package_img": package.package_img,  # Relative path to the package image
        "estimated_prices": [
            {"description": ep.description, "estimated_price": str(ep.estimated_price)}
            for ep in package.estimated_prices
        ],
        "inclusions": [{"inclusion": inc.inclusion} for inc in package.inclusions],
        "exclusions": [{"exclusion": exc.exclusion} for exc in package.exclusions],
        "itineraries": [
            {"title": itin.title, "subtitle": itin.subtitle} for itin in package.itineraries
        ],
    }
    return jsonify(package_data)


@touroperator.route('/delete_tour_package/<int:package_id>', methods=['DELETE'])
@login_required
def delete_tour_package(package_id):
    package = TourPackage.query.get_or_404(package_id)

    # Check if the current user owns the package
    if package.toperator_id != current_user.tour_operator.id:
        return jsonify({"error": "Unauthorized"}), 403

    try:
        # Delete related records first due to foreign key constraints
        EstimatedPrice.query.filter_by(package_id=package.id).delete()
        Inclusion.query.filter_by(package_id=package.id).delete()
        Exclusion.query.filter_by(package_id=package.id).delete()
        Itinerary.query.filter_by(package_id=package.id).delete()

        # Delete the package itself
        db.session.delete(package)
        db.session.commit()
        return jsonify({"success": True, "message": "Tour package deleted successfully."})
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500


@touroperator.route('/edit_tour_package/<int:package_id>', methods=['POST'])
@login_required
def edit_tour_package(package_id):
    package = TourPackage.query.get_or_404(package_id)

    # Check if the current user owns the package
    if package.toperator_id != current_user.tour_operator.id:
        flash("Unauthorized action.", "error")
        return redirect(url_for('touroperator.touroperator_dashboard'))

    package_form = TourPackageForm()

    # Handle file upload
    file = package_form.package_img.data
    filename = package.package_img  # Default to the existing filename

    if file:
        # Secure the filename to avoid path injection
        filename = secure_filename(file.filename)
        # Save the file to the specific upload folder
        package_upload_folder = os.path.join(current_app.root_path, 'static/package_pics')
        file_path = os.path.join(package_upload_folder, filename)
        file.save(file_path)
        filename = f"package_pics/{filename}"  # Store relative path

    # Update the main TourPackage instance
    package.name = package_form.name.data
    package.description = package_form.description.data
    package.package_img = filename

    # Remove old entries before adding new ones
    EstimatedPrice.query.filter_by(package_id=package.id).delete()
    Inclusion.query.filter_by(package_id=package.id).delete()
    Exclusion.query.filter_by(package_id=package.id).delete()
    Itinerary.query.filter_by(package_id=package.id).delete()

    # Process Estimated Price entries
    estimated_price_descriptions = request.form.getlist('estimated_price_description[]')
    estimated_price_values = request.form.getlist('estimated_price_value[]')
    for desc, price in zip(estimated_price_descriptions, estimated_price_values):
        if desc and price:
            estimated_price = EstimatedPrice(
                package_id=package.id, description=desc, estimated_price=price
            )
            db.session.add(estimated_price)

    # Process Inclusions
    inclusions = request.form.getlist('inclusions[]')
    for inclusion_text in inclusions:
        if inclusion_text:
            inclusion = Inclusion(package_id=package.id, inclusion=inclusion_text)
            db.session.add(inclusion)

    # Process Exclusions
    exclusions = request.form.getlist('exclusions[]')
    for exclusion_text in exclusions:
        if exclusion_text:
            exclusion = Exclusion(package_id=package.id, exclusion=exclusion_text)
            db.session.add(exclusion)

    # Process Itinerary
    itinerary_titles = request.form.getlist('itinerary_title[]')
    itinerary_subtitles = request.form.getlist('itinerary_subtitle[]')
    for title, subtitle in zip(itinerary_titles, itinerary_subtitles):
        if title and subtitle:
            itinerary = Itinerary(
                package_id=package.id, title=title, subtitle=subtitle
            )
            db.session.add(itinerary)

    db.session.commit()
    flash("Tour package updated successfully!", "success")
    return redirect(url_for('touroperator.touroperator_dashboard'))


@touroperator.route('/create_tourguide', methods=['GET', 'POST'])
@login_required
def create_tourguide():
    guide_form = UserTourGuideForm()

    if guide_form.validate_on_submit():
        # Create a new User instance for the tour guide
        
        hashed_password = bcrypt.generate_password_hash(guide_form.password.data).decode('utf-8')
        
        new_tourguide_user = User(
            first_name=guide_form.fname.data,
            last_name=guide_form.lname.data,
            email=guide_form.email.data,
            role='tourguide'
        )
        new_tourguide_user.set_password(guide_form.password.data)  # Use the set_password method to hash the password

        try:
            # Add the new tour guide user to the database
            db.session.add(new_tourguide_user)
            db.session.flush()
            # Flush to generate the new user's ID without committing yet

            # Retrieve the TourOperator associated with the current user
            tour_operator = TourOperator.query.filter_by(user_id=current_user.id).first()
            if not tour_operator:
                flash("Error: Current user is not a valid tour operator.", 'danger')
                db.session.rollback()  # Rollback any pending changes
                return redirect(url_for('touroperator.touroperator_dashboard'))

            # Debugging: Check if the tour operator is retrieved correctly
            print(f"Tour Operator ID: {tour_operator.id}")

            # Create the TourGuide entry associated with the new User and TourOperator
            new_tourguide_record = TourGuide(
                user_id=new_tourguide_user.id,
                toperator_id=tour_operator.id,
                contact_num=guide_form.contact_number.data,
            )
            db.session.add(new_tourguide_record)
            db.session.commit()  # Commit both the User and TourGuide entries
            send_confirmation_email(new_tourguide_user)

            # Success message and redirect
            flash('Tour Guide account created successfully!', 'success')
            return redirect(url_for('main.pending_confirmation'))

        except Exception as e:
            # Rollback in case of error and log for debugging
            db.session.rollback()
            # flash('An error occurred while creating the account. Please try again.', 'danger')
            print(f"Database error: {e}")  # Debugging information

    # Render the tour operator dashboard with the form
    return render_template('touroperator_dashboard.html', guide_form=guide_form)




# @touroperator.route('/dashboard')
# @login_required
# def touroperator_dashboard():
#     # Ensure only tour operators can access this page
#     if current_user.role != 'touroperator':
#         flash('You do not have permission to access this page.', 'danger')
#         return redirect(url_for('main.home'))
    
#     guide_form = UserTourGuideForm()  # Instantiate the form for the dashboard
#     package_form = TourPackageForm()
#     tour_guides = TourGuide.query.filter_by(toperator_id=current_user.tour_operator.id).all()
#     packages = TourPackage.query.filter_by(toperator_id=current_user.tour_operator.id).all()
#     operator = TourOperator.query.filter_by(user_id=current_user.id).first()
    
#     return render_template('touroperator_dashboard.html', title='TourOperator Dashboard', guide_form=guide_form, tour_guides=tour_guides
#                            ,package_form=package_form,packages=packages,operator=operator)
@touroperator.route('/dashboard', methods=['GET'])
@login_required
def touroperator_dashboard():
    # Ensure only tour operators can access this page
    if current_user.role != 'touroperator':
        flash('You do not have permission to access this page.', 'danger')
        return redirect(url_for('main.home'))

    guide_form = UserTourGuideForm()  # Instantiate the form for the dashboard
    package_form = TourPackageForm()
    operator = TourOperator.query.filter_by(user_id=current_user.id).first()
    packages = TourPackage.query.filter_by(toperator_id=current_user.tour_operator.id).all()

    # Fetch all tour guides under the current operator
    tour_guides = TourGuide.query.filter_by(toperator_id=operator.id).all()

    # Get the tour_guide_id filter from the query parameters
    tour_guide_id = request.args.get('tour_guide_id', type=int)

    # Set pagination variables
    page = request.args.get('page', 1, type=int)
    per_page = 8  # Number of reviews per page

    # Base query for reviews
    reviews_query = ReviewsRating.query.join(TourGuide).filter(
        TourGuide.toperator_id == operator.id
    )

    # Apply tour_guide_id filter if provided
    if tour_guide_id:
        reviews_query = reviews_query.filter(ReviewsRating.tour_guide_id == tour_guide_id)

    # Paginate the reviews
    paginated_reviews = reviews_query.order_by(ReviewsRating.datetime.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    # Prepare reviews data for rendering
    reviews_data = []
    for review in paginated_reviews.items:
        review_image = ReviewImages.query.filter_by(rr_id=review.id).first()
        tour_image_path = f"review_pics/{review_image.img}" if review_image else 'default.jpg'
        reviews_data.append({
            "traveler_name": f"{review.user.first_name} {review.user.last_name}",
            "traveler_profile": url_for('static', filename=f"profile_pics/{review.user.profile_img}"),
            "rating": review.rating,
            "comment": review.comment,
            "review_date": review.datetime.strftime('%b. %d, %Y'),
            "tour_guide_name": f"{review.tour_guide.user.first_name} {review.tour_guide.user.last_name}",
           "tour_image": url_for('static', filename=tour_image_path)  # Ensure correct image path
        })

    # Prepare pagination data
    pagination_data = {
        "current_page": paginated_reviews.page,
        "total_pages": paginated_reviews.pages,
        "has_next": paginated_reviews.has_next,
        "has_prev": paginated_reviews.has_prev,
        "next_page": paginated_reviews.next_num,
        "prev_page": paginated_reviews.prev_num
    }

    return render_template(
        'touroperator_dashboard.html',
        title='TourOperator Dashboard',
        guide_form=guide_form,
        package_form=package_form,
        tour_guides=tour_guides,
        operator=operator,
        reviews=reviews_data,
        pagination=pagination_data,
        total_reviews=paginated_reviews.total,
        packages=packages,
        selected_tour_guide_id=tour_guide_id  # Pass the selected guide ID for dropdown selection
    )




@touroperator.route('/logout')
@login_required
def logout():
    logout_user()
    session.clear()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('main.home'))


@touroperator.route('/tourguide_profile/<int:guide_id>', methods=['GET'])
@login_required
def tourguide_profile(guide_id):
    # Retrieve the tour guide by ID
    tourguide = User.query.get_or_404(guide_id)
    
    # Pass the tour guide data to the profile template
    return render_template('tourguide_profile.html', tourguide=tourguide)


@touroperator.route('/tourguide/update-name', methods=['POST'])
@login_required
def update_name():
    data = request.get_json()
    new_name = data.get('name')
    current_user.name = new_name
    db.session.commit()
    return jsonify({"success": True})



@touroperator.route('/update_contact_number', methods=['POST'])
@login_required
def update_contact_number():
    data = request.get_json()
    new_contact_number = data.get('contact_number')

    # Validate that a contact number is provided and is in the correct format
    if not new_contact_number:
        return jsonify({'success': False, 'error': 'Contact number is required.'}), 400
    if not new_contact_number.isdigit() or len(new_contact_number) < 7:
        return jsonify({'success': False, 'error': 'Invalid contact number format. Please enter a valid number.'}), 400

    try:
        # Assuming the `TourOperator` model is related to the `User` model with `tour_operator` relationship
        tour_operator = current_user.tour_operator
        if not tour_operator:
            return jsonify({'success': False, 'error': 'Tour operator profile not found.'}), 404

        # Update the contact number and commit to the database
        tour_operator.contact_num = new_contact_number
        db.session.commit()
        return jsonify({'success': True, 'message': 'Contact number updated successfully.'}), 200

    except Exception as e:
        db.session.rollback()  # Rollback in case of an error
        print(f"Error updating contact number: {e}")  # Log error for debugging
        return jsonify({'success': False, 'error': 'An error occurred while updating the contact number. Please try again later.'}), 500
