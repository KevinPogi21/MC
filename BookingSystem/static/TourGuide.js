// Get elements
const sidebarToggle = document.getElementById('sidebar-toggle');
const sideNav = document.getElementById('side-nav');
const navLinks = document.querySelectorAll('.nav-link');
const tabPanes = document.querySelectorAll('.tab-pane');

// Logout modal elements
const logoutModal = document.getElementById('logout-modal');
const logoutOverlay = document.getElementById('logout-overlay');
const confirmLogoutBtn = document.getElementById('confirm-logout-btn');
const cancelLogoutBtn = document.getElementById('cancel-logout-btn');
const mainContent = document.querySelector('.tab-content'); // The main content area

// Toggle Sidebar on Mobile
sidebarToggle?.addEventListener('click', () => {
  sideNav.classList.toggle('active');
});

// Handle tab switching and show logout modal
navLinks.forEach((link) => {
  link.addEventListener('click', (e) => {
    e.preventDefault();

    const targetTab = link.dataset.tab;

    if (targetTab === 'logout') {
      showLogoutModal(); // Show the logout modal
    } else {
      switchActiveTab(targetTab); // Switch to the clicked tab
    }

    // Close the sidebar if on mobile
    if (window.innerWidth <= 768) {
      sideNav.classList.remove('active');
    }
  });
});

// Switch active tabs
function switchActiveTab(targetTab) {
  navLinks.forEach((link) => link.classList.remove('active'));
  document.querySelector(`[data-tab="${targetTab}"]`).classList.add('active');

  tabPanes.forEach((pane) => {
    pane.style.display = pane.id === targetTab ? 'block' : 'none';
  });
}


// Show Logout Modal and Overlay
function showLogoutModal() {
  logoutModal.classList.add('show');
  logoutOverlay.classList.add('show');
  mainContent.classList.add('blurred'); // Apply blur effect to main content
}

// Hide Logout Modal and Remove Overlay
function hideLogoutModal() {
  logoutModal.classList.remove('show');
  logoutOverlay.classList.remove('show');
  mainContent.classList.remove('blurred'); // Remove blur effect
}

// Confirm Logout and Redirect
confirmLogoutBtn.addEventListener('click', () => {
  window.location.href = 'Traveler - TGList.html'; // Redirect to homepage
});

// Cancel Logout and Close Modal
cancelLogoutBtn.addEventListener('click', hideLogoutModal);

// Handle Logout Link Click
document.querySelector('[data-tab="logout"]').addEventListener('click', (e) => {
  e.preventDefault();
  showLogoutModal();
});



// Ensure Profile Tab Displays on Load
window.addEventListener('DOMContentLoaded', () => {
  tabPanes.forEach((pane) => {
    pane.style.display = pane.id === 'profile' ? 'block' : 'none';
  });
});










// Editable About Me Section
document.addEventListener('DOMContentLoaded', async function () {
  // About Me Section Elements
  const editAboutBtn = document.getElementById('edit-about-btn');
  const saveAboutBtn = document.getElementById('save-about-btn');
  const aboutText = document.getElementById('about-text');

  // Load existing data from server on page load
  async function loadInitialData() {
    try {
      const response = await fetch('/tourguide/get_profile_data');
      const data = await response.json();

      if (data.success) {
        const profileData = data.profile_data;
        
        // Populate initial data
        if (profileData.about_me) aboutText.value = profileData.about_me;
        if (profileData.characteristics) updateDisplayList(document.getElementById('characteristics-list'), profileData.characteristics);
        if (profileData.skills) updateDisplayList(document.getElementById('skills-list'), profileData.skills);
      } else {
        console.error('Failed to load initial data:', data.message);
      }
    } catch (error) {
      console.error("Error loading initial data:", error);
    }
  }

  loadInitialData();

  // Toggle About Me Edit Mode
  editAboutBtn.addEventListener('click', () => toggleEdit(aboutText, editAboutBtn, saveAboutBtn));
  saveAboutBtn.addEventListener('click', async () => {
    const updatedBio = aboutText.value;
    if (!updatedBio.trim()) {
      alert("Please enter text for 'About Me'");
      return;
    }
    try {
      const response = await fetch('/tourguide/update_about_me', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ bio: updatedBio })
      });
      const result = await response.json();
      if (result.success) {
        alert('About Me updated successfully!');
      } else {
        alert('Failed to update About Me.');
      }
    } catch (error) {
      console.error('Error saving About Me:', error);
      alert('An error occurred. Please try again.');
    }
    toggleEdit(aboutText, editAboutBtn, saveAboutBtn, false);
  });

  function toggleEdit(input, editBtn, saveBtn, isEditing = true) {
    input.disabled = !isEditing;
    editBtn.classList.toggle('hidden', isEditing);
    saveBtn.classList.toggle('hidden', !isEditing);
    if (isEditing) input.focus();
  }

  // Characteristics and Skills Sections
  function setupEditableList(editBtn, saveBtn, addBtn, list, saveFunction) {
    editBtn.addEventListener('click', () => toggleListEdit(list, true, addBtn, editBtn, saveBtn));
    saveBtn.addEventListener('click', async () => {
      await saveFunction();
      toggleListEdit(list, false, addBtn, editBtn, saveBtn);
    });

    addBtn.addEventListener('click', () => {
      const newItem = createEditableListItem();
      list.appendChild(newItem);
      newItem.querySelector('.editable').focus();
    });
  }

  function createEditableListItem(text = 'New Item') {
    const li = document.createElement('li');
    li.innerHTML = `
      <span class="checkmark">&#10003;</span>
      <span class="editable" contenteditable="true">${text}</span>
      <button class="remove-btn">&#8722;</button>
    `;
    li.querySelector('.remove-btn').addEventListener('click', () => {
      if (confirm("Are you sure you want to remove this item?")) {
        li.remove();
      }
    });
    return li;
  }

  function toggleListEdit(list, isEditing, addBtn, editBtn, saveBtn) {
    Array.from(list.children).forEach((li) => {
      const editableElement = li.querySelector('.editable');
      const removeBtn = li.querySelector('.remove-btn');
      editableElement.contentEditable = isEditing;
      removeBtn.classList.toggle('hidden', !isEditing);
    });
    addBtn.classList.toggle('hidden', !isEditing);
    editBtn.classList.toggle('hidden', isEditing);
    saveBtn.classList.toggle('hidden', !isEditing);
  }

  async function saveCharacteristics() {
    const characteristics = Array.from(document.querySelectorAll('#characteristics-list .editable')).map(item => item.textContent.trim());
    if (characteristics.some(item => !item)) {
      alert("Please ensure all characteristics have content.");
      return;
    }
    try {
      const response = await fetch('/tourguide/update_characteristics', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ characteristics })
      });
      const result = await response.json();
      if (result.success) {
        alert('Characteristics updated successfully!');
        updateDisplayList(document.getElementById('characteristics-list'), characteristics);
      } else {
        alert('Failed to update Characteristics. Please try again.');
      }
    } catch (error) {
      console.error('Error saving Characteristics:', error);
      alert('An error occurred. Please try again.');
    }
  }

  async function saveSkills() {
    const skills = Array.from(document.querySelectorAll('#skills-list .editable')).map(item => item.textContent.trim());
    if (skills.some(item => !item)) {
      alert("Please ensure all skills have content.");
      return;
    }
    try {
      const response = await fetch('/tourguide/update_skills', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ skills })
      });
      const result = await response.json();
      if (result.success) {
        alert('Skills updated successfully!');
        updateDisplayList(document.getElementById('skills-list'), skills);
      } else {
        alert('Failed to update Skills. Please try again.');
      }
    } catch (error) {
      console.error('Error saving Skills:', error);
      alert('An error occurred. Please try again.');
    }
  }

  function updateDisplayList(listElement, items) {
    listElement.innerHTML = '';
    items.forEach(item => {
      const li = createEditableListItem(item);
      li.querySelector('.editable').contentEditable = 'false';
      li.querySelector('.remove-btn').classList.add('hidden');
      listElement.appendChild(li);
    });
  }

  // Initialize Editable Lists with Save Functions
  setupEditableList(
    document.getElementById('edit-char-btn'),
    document.getElementById('save-char-btn'),
    document.getElementById('add-char-btn'),
    document.getElementById('characteristics-list'),
    saveCharacteristics
  );

  setupEditableList(
    document.getElementById('edit-skills-btn'),
    document.getElementById('save-skills-btn'),
    document.getElementById('add-skills-btn'),
    document.getElementById('skills-list'),
    saveSkills
  );
});

















// Price Editing Logic
const editPriceBtn = document.getElementById('edit-price-btn');
const savePriceBtn = document.getElementById('save-price-btn');
const priceDisplay = document.getElementById('tour-price');
const priceInput = document.getElementById('price-input');

// Enable Price Editing
editPriceBtn.addEventListener('click', () => {
    // Hide the display and show the input for editing
    priceDisplay.classList.add('hidden');
    priceInput.classList.remove('hidden');
    priceInput.value = parseFloat(priceDisplay.textContent.replace('₱', '').replace(/,/g, '')); // Populate input, remove commas
    editPriceBtn.classList.add('hidden');
    savePriceBtn.classList.remove('hidden');
});

// Save Edited Price and Send to Backend
savePriceBtn.addEventListener('click', async () => {
    const newPrice = parseFloat(priceInput.value);
    
    // Validate that the input is a positive number
    if (isNaN(newPrice) || newPrice <= 0) {
        alert('Please enter a valid price.');
        return;
    }

    // Update the displayed price in the UI
    priceDisplay.textContent = `₱${newPrice.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    priceDisplay.classList.remove('hidden');
    priceInput.classList.add('hidden');
    editPriceBtn.classList.remove('hidden');
    savePriceBtn.classList.add('hidden');

    // Send the updated price to the backend
    try {
        const response = await fetch('/tourguide/update_price', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ price: newPrice.toFixed(2) })
        });

        const result = await response.json();
        console.log("Server response:", result); // Debugging log

        if (!result.success) {
            alert('Failed to save price. Please try again.');
            // Revert display if saving failed
            priceDisplay.textContent = `₱${parseFloat(priceDisplay.getAttribute('data-original-price')).toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
        } else {
            // Update original price attribute on success
            priceDisplay.setAttribute('data-original-price', newPrice.toFixed(2));
        }
    } catch (error) {
        console.error('Error saving price:', error);
        alert('An error occurred while saving the price.');
    }
});

















// Elements for Profile Activation Modal
document.addEventListener('DOMContentLoaded', async function () {
  const profileToggle = document.getElementById('profile-toggle');
  const toggleStatus = document.getElementById('toggle-status');
  const activationModal = document.getElementById('activation-confirmation-modal');
  const confirmCompleteBtn = document.getElementById('confirm-complete-btn');
  const cancelActivationBtn = document.getElementById('cancel-activation-btn');

  // Fetch and update the initial status of the profile on page load
  await getProfileStatus();

  // Open modal when attempting to activate profile
  profileToggle.addEventListener('click', () => {
    if (toggleStatus.textContent === 'Inactive') {
      openActivationModal();
    } else {
      deactivateProfile();  // Deactivate profile directly
    }
  });

  // Confirm profile activation and send to backend
  confirmCompleteBtn.addEventListener('click', async () => {
    closeActivationModal();
    const success = await activateProfile();  // Attempt to activate via backend
    if (success) {
      profileToggle.classList.add('active');
      toggleStatus.textContent = 'Active';
      alert("Profile activated successfully!");
    } else {
      alert("Profile activation failed. Please ensure all required fields are complete.");
    }
  });

  // Cancel button to close modal
  cancelActivationBtn.addEventListener('click', closeActivationModal);

  // Open and close functions for the activation modal
  function openActivationModal() {
    activationModal.classList.add('show');
  }

  function closeActivationModal() {
    activationModal.classList.remove('show');
  }

  // Activate profile in the backend
  async function activateProfile() {
    try {
      const response = await fetch('/tourguide/activate_profile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      const result = await response.json();
      if (!result.success) {
        console.error("Activation failed:", result.message);
      }
      return result.success;
    } catch (error) {
      console.error("Error activating profile:", error);
      return false;
    }
  }

  // Deactivate profile in the backend
  async function deactivateProfile() {
    try {
      const response = await fetch('/tourguide/deactivate_profile', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
      });
      const result = await response.json();
      if (result.success) {
        profileToggle.classList.remove('active');
        toggleStatus.textContent = 'Inactive';
        alert("Profile deactivated successfully!");
      } else {
        alert("Profile deactivation failed.");
      }
    } catch (error) {
      console.error("Error deactivating profile:", error);
    }
  }

  // Fetch the profile status from the backend on page load
  async function getProfileStatus() {
    try {
      const response = await fetch('/tourguide/get_profile_status');
      const result = await response.json();
      if (result.active) {
        profileToggle.classList.add('active');
        toggleStatus.textContent = 'Active';
      } else {
        profileToggle.classList.remove('active');
        toggleStatus.textContent = 'Inactive';
      }
    } catch (error) {
      console.error("Error fetching profile status:", error);
    }
  }
});






const changePicBtn = document.getElementById('change-pic-btn');
const uploadPicInput = document.getElementById('upload-pic');
const profilePicMain = document.getElementById('profile-pic-main');
const profilePicSecondary = document.getElementById('profile-pic-secondary');
const cropperModal = document.getElementById('cropper-modal');
const cropperContainer = document.getElementById('cropper-container');
const cropBtn = document.getElementById('crop-btn');
const closeCropperBtn = document.getElementById('close-cropper-modal');
const savePicBtn = document.getElementById('save-pic-btn');
let cropper;

// Hide "Save" button by default on page load
savePicBtn.classList.add('hidden');

// Open file input on button click
changePicBtn.addEventListener('click', () => {
  uploadPicInput.value = "";  // Reset file input to allow re-selection
  uploadPicInput.click();
});

// Show cropper modal on image selection
uploadPicInput.addEventListener('change', (event) => {
  const file = event.target.files[0];
  if (file) {
    const reader = new FileReader();
    reader.onload = (e) => {
      const img = document.createElement('img');
      img.src = e.target.result;
      img.id = 'crop-image';
      cropperContainer.innerHTML = ''; // Clear previous image
      cropperContainer.appendChild(img);
      cropperModal.classList.add('show'); // Show the cropper modal

      // Destroy previous cropper instance if it exists, and create a new one
      if (cropper) {
        cropper.destroy();
        cropper = null;  // Ensure cropper is set to null after destruction
      }
      cropper = new Cropper(img, {
        aspectRatio: 1,
        viewMode: 1,
        movable: true,
        zoomable: true,
        scalable: true,
        cropBoxResizable: true,
      });
    };
    reader.readAsDataURL(file);
  }
});

// Crop and update profile picture preview
cropBtn.addEventListener('click', () => {
  const canvas = cropper.getCroppedCanvas({ width: 200, height: 200 });
  if (canvas) {
    // Update both profile picture previews
    const newImageSrc = canvas.toDataURL();
    profilePicMain.src = newImageSrc;
    profilePicSecondary.src = newImageSrc;

    cropperModal.classList.remove('show'); // Close modal
    savePicBtn.classList.remove('hidden'); // Show save button only after cropping
  } else {
    console.error("Error: Cropping failed. Canvas is not generated.");
  }
});

// Close cropper modal and destroy cropper instance
closeCropperBtn.addEventListener('click', () => {
  if (cropper) {
    cropper.destroy();
    cropper = null;  // Set cropper to null to ensure clean reinitialization
  }
  cropperModal.classList.remove('show');
});

// Save profile picture to backend
savePicBtn.addEventListener('click', () => {
  cropper.getCroppedCanvas({ width: 200, height: 200 }).toBlob((blob) => {
    const formData = new FormData();
    formData.append('profile_picture', blob);

    console.log("Uploading profile picture...");

    fetch('/tourguide/upload_profile_picture', {
      method: 'POST',
      body: formData
    })
    .then(response => response.json())
    .then(data => {
      console.log("Server response:", data);

      if (data.success) {
        // Append a timestamp to prevent caching issues and update both profile pictures in the UI
        const newImageUrl = `${data.url}?t=${new Date().getTime()}`;
        profilePicMain.src = newImageUrl;
        profilePicSecondary.src = newImageUrl;

        savePicBtn.classList.add('hidden'); // Hide save button after saving
        alert('Profile picture saved successfully!');
      } else {
        alert('Failed to save profile picture.');
      }
    })
    .catch(error => {
      console.error('Error uploading image:', error);
      alert('An error occurred while saving the picture.');
    })
    .finally(() => {
      // Ensure the cropper instance is destroyed after saving
      if (cropper) {
        cropper.destroy();
        cropper = null;
      }
      cropperModal.classList.remove('show');
    });
  });
});


























// Variables for Notification Interaction
// Tour Guide Side
// This code is for the **Tour Guide Side**
const notificationPanel = document.querySelector('.notification-list');
const viewNotificationDetails = (notificationText) => {
  alert(`Notification Details: ${notificationText}`);
};




















// Get elements
const toggleTabsBtn = document.getElementById('toggle-tabs-btn');
const bookingsTabs = document.getElementById('bookings-tabs');
const bookingTabBtns = document.querySelectorAll('.booking-tab-btn');
const bookingCategories = document.querySelectorAll('.booking-category');



// Check screen size and adjust visibility
function adjustTabsForScreenSize() {
  if (window.innerWidth > 768) {
    // Show tabs and hide the toggle button on larger screens
    bookingsTabs.classList.remove('hidden');
    toggleTabsBtn.style.display = 'none';
  } else {
    // Hide tabs and show the toggle button on mobile screens
    bookingsTabs.classList.add('hidden');
    toggleTabsBtn.style.display = 'block';
  }
}

// Toggle tabs visibility on mobile screens
toggleTabsBtn.addEventListener('click', () => {
  bookingsTabs.classList.toggle('hidden');
  toggleTabsBtn.textContent = bookingsTabs.classList.contains('hidden') ? 'Show Tabs' : 'Hide Tabs';
});

// Handle tab selection and auto-collapse on mobile
bookingTabBtns.forEach((btn) => {
  btn.addEventListener('click', () => {
    // Set active tab
    bookingTabBtns.forEach((btn) => btn.classList.remove('active'));
    btn.classList.add('active');

    const status = btn.dataset.status;

    // Show/Hide booking categories based on tab selection
    bookingCategories.forEach((category) => {
      const categoryStatus = category.dataset.status;
      category.style.display = status === 'all' || categoryStatus === status ? 'block' : 'none';
    });

    // Collapse the tabs if on mobile
    if (window.innerWidth <= 768) {
      bookingsTabs.classList.add('hidden');
      toggleTabsBtn.textContent = 'Show Tabs'; // Reset button text
    }
  });
});

// Initial check and add event listener to adjust on window resize
adjustTabsForScreenSize();
window.addEventListener('resize', adjustTabsForScreenSize);




// Booking Details Modal Logic
const bookingModal = document.getElementById('booking-modal');
const bookingInfo = document.getElementById('booking-info');
const closeBookingModal = document.getElementById('close-booking-modal');

function openBookingDetails(details) {
  bookingInfo.textContent = details;
  bookingModal.classList.add('show');
}

closeBookingModal.addEventListener('click', () => {
  bookingModal.classList.remove('show');
});









//CALENDAR
document.addEventListener('DOMContentLoaded', function () {
  const calendarEl = document.getElementById('availability-calendar');
  const editAvailabilityBtn = document.getElementById('edit-availability');
  const markAvailableBtn = document.getElementById('mark-available');
  const markUnavailableBtn = document.getElementById('mark-unavailable');
  const resetCalendarBtn = document.getElementById('reset-calendar');
  const saveAvailabilityBtn = document.getElementById('save-availability');

  let isEditing = false;
  let selectedDate = null;

  //const tourGuideId = calendarEl.getAttribute('data-tour-guide-id');

  // Initialize FullCalendar for tour guide's availability management
  const calendar = new FullCalendar.Calendar(calendarEl, {
    initialView: 'dayGridMonth',
    selectable: true,
    selectOverlap: false,
    headerToolbar: {
      left: 'prev,next today',
      center: 'title',
      right: 'dayGridMonth,timeGridWeek,timeGridDay',
    },
    events: [],
    select: function (info) {
      if (isEditing) {
        const existingEvent = findEventByDate(info.startStr);
        if (!existingEvent) selectedDate = info.startStr;
        else alert('This date already has a status.');
        calendar.unselect();
      } else {
        alert('Enable edit mode to mark availability.');
      }
    },
    eventClick: function (info) {
      if (isEditing && info.event.extendedProps.status !== 'booked') {
        info.event.remove();
      } else if (info.event.extendedProps.status === 'booked') {
        alert('This date is booked and cannot be changed.');
      }
    },

    
  });
  


  calendar.render();

  // Load availability and set FullCalendar
  async function loadAvailability() {
    const tourGuideId = "{{ tour_guide_id }}"
 // Update this as necessary to dynamically retrieve the ID
    try {
        console.log(`Fetching availability data from URL: /tourguide/get_availability/${tourGuideId}`);
        
        const response = await fetch(`/tourguide/get_availability/${tourGuideId}`);
        
        if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
        
        const availability = await response.json();
        console.log("Fetched availability data:", availability);

        if (!calendar) {
            throw new Error("Calendar instance is not defined.");
        }

        // Clear current events to avoid duplication
        calendar.getEvents().forEach(event => event.remove());

        // Populate FullCalendar with fetched availability data
        availability.forEach(entry => {
            const color = entry.status === 'available' ? '#4ecdc4' : '#e63946';
            const title = entry.status === 'available' ? 'Available' : 'Unavailable';
            calendar.addEvent({
                title: title,
                start: entry.date,
                allDay: true,
                backgroundColor: color,
                textColor: 'white',
                extendedProps: { status: entry.status },
            });
        });
    } catch (error) {
        console.error("Error loading availability:", error);
    }
  }

  loadAvailability(); // Call to load availability on page load

  // Helper function to find if an event exists by date
  function findEventByDate(date) {
    return calendar.getEvents().find(event => event.startStr === date);
  }

  // Toggle edit mode and show/hide controls
  editAvailabilityBtn.addEventListener('click', () => {
    isEditing = !isEditing;
    toggleEditButtons(isEditing);
  });

  function toggleEditButtons(isEditing) {
    markAvailableBtn.classList.toggle('hidden', !isEditing);
    markUnavailableBtn.classList.toggle('hidden', !isEditing);
    resetCalendarBtn.classList.toggle('hidden', !isEditing);
    saveAvailabilityBtn.classList.toggle('hidden', !isEditing);
    editAvailabilityBtn.textContent = isEditing ? 'Exit Edit Mode' : 'Edit Availability';
  }

  // Mark selected date as available
  markAvailableBtn.addEventListener('click', () => {
    if (selectedDate) {
      addEvent('Available', selectedDate, '#4ecdc4', 'available');
      selectedDate = null;
    }
  });

  // Mark selected date as unavailable
  markUnavailableBtn.addEventListener('click', () => {
    if (selectedDate) {
      addEvent('Unavailable', selectedDate, '#e63946', 'unavailable');
      selectedDate = null;
    }
  });

  // Add event to the calendar with title, color, and status
  function addEvent(title, date, color, status) {
    if (!findEventByDate(date)) {
      calendar.addEvent({
        title: title,
        start: date,
        allDay: true,
        backgroundColor: color,
        textColor: 'white',
        extendedProps: { status: status },
      });
    } else {
      alert('This date already has a status.');
    }
  }

  // Reset calendar events, excluding booked ones
  resetCalendarBtn.addEventListener('click', async () => {
    const tourGuideId = 28; // Use the actual tour guide ID here
  
    // Call the backend to clear availability
    try {
      const response = await fetch(`/tourguide/clear_availability/${tourGuideId}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
  
      if (response.ok) {
        // Clear the calendar in the frontend
        calendar.getEvents().forEach(event => {
          if (event.extendedProps.status !== 'booked') event.remove();
        });
  
        alert('Calendar reset successfully!');
      } else {
        alert('Failed to reset calendar.');
      }
    } catch (error) {
      console.error('Error resetting calendar:', error);
      alert('An error occurred. Please try again.');
    }
  });

  // Save availability data to backend
  saveAvailabilityBtn.addEventListener('click', async () => {
    const savedAvailability = calendar.getEvents().map(event => ({
      title: event.title,
      start: event.startStr,
      status: event.extendedProps.status,
    }));

    console.log("Saving availability data:", savedAvailability);

    try {
      const response = await fetch('/tourguide/set_availability', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(savedAvailability),
      });

      if (response.ok) {
        alert('Availability saved successfully!');
        loadAvailability(); // Reload availability after saving to refresh the calendar
      } else {
        alert('Failed to save availability.');
      }
    } catch (error) {
      console.error('Error saving availability:', error);
    }
  });
});





















// Elements
// Elements EMAIL and Contact number and PASSWORD
document.addEventListener('DOMContentLoaded', function () {
  // Elements
  const guideEditEmailBtn = document.getElementById('guide-edit-email-btn');
  const guideEditContactBtn = document.getElementById('guide-edit-contact-btn');
  const guideEditPasswordBtn = document.getElementById('guide-edit-password-btn'); // Pencil icon for password change
  const guidePasswordModal = document.getElementById('guide-password-confirm-modal'); // Password verification modal
  const guideChangePasswordModal = document.getElementById('guide-change-password-modal'); // Change password modal
  const guideChangeEmailModal = document.getElementById('guide-change-email-modal'); // Change email modal
  const guideChangeContactModal = document.getElementById('guide-change-contact-modal'); // Change contact modal
  const guidePasswordCancelBtn = document.getElementById('guide-password-cancel-btn');
  const guidePasswordConfirmBtn = document.getElementById('guide-password-confirm-btn');
  const verifyPasswordInput = document.getElementById('guide-confirm-password-input');
  const newPasswordInput = document.getElementById('guide-new-password');
  const confirmNewPasswordInput = document.getElementById('guide-confirm-new-password');
  const guideCancelPasswordBtn = document.getElementById('guide-cancel-password-btn');
  const guideSavePasswordBtn = document.getElementById('guide-save-password-btn');
  const emailInput = document.getElementById('email');
  const guideSaveEmailBtn = document.getElementById('guide-save-email-btn');
  const guideCancelEmailBtn = document.getElementById('guide-cancel-email-btn');
  const contactNumberInput = document.getElementById('contact-number');
  const guideNewContactInput = document.getElementById('guide-new-contact-input');
  const guideSaveContactBtn = document.getElementById('guide-save-contact-btn');
  const guideCancelContactBtn = document.getElementById('guide-cancel-contact-btn');
  const modalOverlay = document.getElementById('modal-overlay');
  
  let activeAction = ''; // Track the current action: 'email', 'contact', or 'password'

  // Function to show the password confirmation modal with overlay
  function openGuidePasswordModal(action) {
      activeAction = action;
      guidePasswordModal.classList.add('show');
      modalOverlay.classList.add('show');
  }

  // Function to close the password modal
  function closeGuidePasswordModal() {
      guidePasswordModal.classList.remove('show');
      modalOverlay.classList.remove('show');
      verifyPasswordInput.value = ''; // Clear password input field
  }

  // Function to show the specific modal based on action
  function openActionModal() {
      if (activeAction === 'email') {
          guideChangeEmailModal.classList.add('show');
      } else if (activeAction === 'contact') {
          guideChangeContactModal.classList.add('show');
      } else if (activeAction === 'password') {
          guideChangePasswordModal.classList.add('show');
      }
      modalOverlay.classList.add('show');
  }

  // Function to close all action modals
  function closeActionModals() {
      guideChangeEmailModal.classList.remove('show');
      guideChangeContactModal.classList.remove('show');
      guideChangePasswordModal.classList.remove('show');
      modalOverlay.classList.remove('show');
      newPasswordInput.value = '';
      confirmNewPasswordInput.value = '';
  }

  // Open the password verification modal on edit email, contact, or password button click
  guideEditEmailBtn.addEventListener('click', () => openGuidePasswordModal('email'));
  guideEditContactBtn.addEventListener('click', () => openGuidePasswordModal('contact'));
  guideEditPasswordBtn.addEventListener('click', () => openGuidePasswordModal('password'));

  // Close the password verification modal on cancel button click
  guidePasswordCancelBtn.addEventListener('click', closeGuidePasswordModal);

  // Verify password and open the appropriate modal if successful
  guidePasswordConfirmBtn.addEventListener('click', async () => {
    const password = verifyPasswordInput.value.trim();

    try {
      // Send request to verify the password
      const response = await fetch('/tourguide/verify_password', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json'
          },
          body: JSON.stringify({ password: password })
      });

      const result = await response.json();

      console.log("Password verification result:", result); // Debugging output

      if (result.success) {
          // Password is verified, close password modal and open the respective modal
          closeGuidePasswordModal();
          alert("Password verified successfully!"); // Show verification success message
          openActionModal(); // Only open the action modal if verification is successful
      } else {
          alert(result.message || 'Password verification failed. Please try again.');
      }
    } catch (error) {
      console.error('Error verifying password:', error);
      alert('There was an error verifying your password. Please try again.');
    }
  });

  // Close the email and contact modals on cancel buttons
  guideCancelEmailBtn.addEventListener('click', closeActionModals);
  guideCancelContactBtn.addEventListener('click', closeActionModals);
  guideCancelPasswordBtn.addEventListener('click', closeActionModals);

  // Save the updated email to the backend
  guideSaveEmailBtn.addEventListener('click', async () => {
    const newEmail = document.getElementById('guide-new-email-input').value.trim();

    if (!newEmail || !newEmail.includes('@')) {
        alert('Please enter a valid email address.');
        return;
    }

    try {
      const response = await fetch('/tourguide/update_email', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ email: newEmail })
      });
      const result = await response.json();
  
      if (result.success) {
        const emailInput = document.getElementById('email-input'); // Ensure ID matches the actual input ID
        if (emailInput) {
          emailInput.value = newEmail; // Update displayed email
        } else {
          console.error("Email input element not found in the DOM.");
        }
        closeActionModals();
        alert('Email updated successfully!');
      } else {
        alert(result.message || 'Failed to update email. Please try again.');
      }
    } catch (error) {
      console.error("Error updating email:", error);
      alert('There was an error processing your request. Please try again.');
    }
  });

  // Save the updated contact number to the backend
  guideSaveContactBtn.addEventListener('click', async () => {
    const newContactNumber = guideNewContactInput.value.trim();

    if (!newContactNumber || isNaN(newContactNumber) || newContactNumber.length < 7) {
        alert('Please enter a valid contact number.');
        return;
    }

    try {
      const response = await fetch('/tourguide/update_contact_number', {
          method: 'POST',
          headers: {
              'Content-Type': 'application/json'
          },
          body: JSON.stringify({ contact_number: newContactNumber })
      });

      const result = await response.json();

      if (result.success) {
          contactNumberInput.value = newContactNumber; // Update displayed contact number
          closeActionModals();
          alert('Contact number updated successfully!');
      } else {
          alert(result.message || 'Failed to update contact number. Please try again.');
      }
    } catch (error) {
      console.error('Error updating contact number:', error);
      alert('There was an error processing your request. Please try again.');
    }
  });

  // Save the new password to the backend
  guideSavePasswordBtn.addEventListener('click', async () => {
    const newPassword = newPasswordInput.value.trim();
    const confirmNewPassword = confirmNewPasswordInput.value.trim();

    // Validate the new password inputs
    if (!newPassword || !confirmNewPassword) {
      alert('Please fill out all password fields.');
      return;
    }
    if (newPassword !== confirmNewPassword) {
      alert('New passwords do not match.');
      return;
    }
    if (newPassword.length < 8) {
      alert('New password should be at least 8 characters long.');
      return;
    }

    try {
      // Send a request to update the password
      const response = await fetch('/tourguide/update_password', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ new_password: newPassword })
      });

      const result = await response.json();

      if (result.success) {
        alert('Password updated successfully!');
        closeActionModals(); // Close the modal on success
      } else {
        alert(result.message || 'Failed to update password. Please try again.');
      }
    } catch (error) {
      console.error('Error updating password:', error);
      alert('There was an error processing your request. Please try again.');
    }
  });
});









// Confirm password and open the appropriate modal for editing
document.addEventListener('DOMContentLoaded', function () {
  // Select the elements
  const guidePasswordConfirmBtn = document.getElementById('guide-password-confirm-btn');
  const guideConfirmPasswordInput = document.getElementById('guide-confirm-password-input');

  if (!guidePasswordConfirmBtn || !guideConfirmPasswordInput) {
      console.error('One or more elements not found.');
      return;
  }

  let guideActiveAction = ''; // Define this variable somewhere in scope to track action

  // Add event listener
  guidePasswordConfirmBtn.addEventListener('click', () => {
      // if (guideConfirmPasswordInput.value === 'password123') { // Replace 'password123' with actual logic to validate the password
      //     closeGuideModal();
      //     if (guideActiveAction === 'email') {
      //         openGuideChangeEmailModal();
      //     } else if (guideActiveAction === 'password') {
      //         openGuideChangePasswordModal();
      //     } else if (guideActiveAction === 'contact') {
      //         openGuideChangeContactModal();
      //     }
      // } else {
      //     alert('Incorrect password. Please try again.');
      // }
  });

  function closeGuideModal() {
      // Your function to close the password confirmation modal
      console.log('Closing password modal');
      // Actual code to close the modal goes here
  }

  function openGuideChangeEmailModal() {
      // Function to open the email change modal
      console.log('Opening email change modal');
      // Code to open the email modal goes here
  }

  function openGuideChangePasswordModal() {
      // Function to open the password change modal
      console.log('Opening password change modal');
      // Code to open the password modal goes here
  }

  function openGuideChangeContactModal() {
      // Function to open the contact change modal
      console.log('Opening contact change modal');
      // Code to open the contact modal goes here
  }
});






















// Save new email
document.addEventListener('DOMContentLoaded', function () {
  // Select the guideSaveEmailBtn element
  const guideSaveEmailBtn = document.getElementById('guide-save-email-btn');
  const guideNewEmailInput = document.getElementById('guide-new-email-input');
  
  if (!guideSaveEmailBtn || !guideNewEmailInput) {
      console.error('Element not found in the DOM.');
      return;
  }

  // Add event listener for the save button
  guideSaveEmailBtn.addEventListener('click', () => {
      const newEmail = guideNewEmailInput.value;
      alert(`New email saved: ${newEmail}`);
      closeGuideModal(); // Ensure this function is defined
  });
});

// Example function to close the modal (make sure this function is defined in your script)
function closeGuideModal() {
  const modal = document.getElementById('guide-change-email-modal');
  if (modal) {
      modal.classList.add('hidden');
  }
}













// Save new password
document.addEventListener('DOMContentLoaded', function () {
  // Select the elements
  const guideSavePasswordBtn = document.getElementById('guide-save-password-btn');
  const newPasswordInput = document.getElementById('guide-new-password');
  const confirmNewPasswordInput = document.getElementById('guide-confirm-new-password');

  // Check if elements exist before adding event listeners
  if (!guideSavePasswordBtn || !newPasswordInput || !confirmNewPasswordInput) {
      console.error('One or more elements not found in the DOM.');
      return;
  }

  // Add event listener for the save password button
  guideSavePasswordBtn.addEventListener('click', () => {
      const newPassword = newPasswordInput.value;
      const confirmPassword = confirmNewPasswordInput.value;

      if (newPassword === confirmPassword) {
          alert('Password changed successfully!');
          closeGuideModal(); // Ensure this function is defined
      } else {
          alert('Passwords do not match.');
      }
  });
});

// Example function to close the modal (make sure this function is defined in your script)
function closeGuideModal() {
  const modal = document.getElementById('guide-change-password-modal');
  if (modal) {
      modal.classList.add('hidden');
  }
}














// Save new contact number



// Cancel and close modal actions
document.addEventListener('DOMContentLoaded', function () {
  // Get elements
  const guidePasswordCancelBtn = document.getElementById('guide-password-cancel-btn');
  const guideCancelEmailBtn = document.getElementById('guide-cancel-email-btn');
  const guideCancelPasswordBtn = document.getElementById('guide-cancel-password-btn');
  const guideCancelContactBtn = document.getElementById('guide-cancel-contact-btn');
  const modalOverlay = document.getElementById('modal-overlay');
  
  // Check if elements exist before adding event listeners
  if (!guidePasswordCancelBtn || !guideCancelEmailBtn || !guideCancelPasswordBtn || !modalOverlay) {
      console.error('One or more elements are missing from the DOM');
      return;
  }

  // Add event listeners to close modals
  guidePasswordCancelBtn.addEventListener('click', closeGuideModal);
  guideCancelEmailBtn.addEventListener('click', closeGuideModal);
  guideCancelPasswordBtn.addEventListener('click', closeGuideModal);
  guideCancelContactBtn?.addEventListener('click', closeGuideModal); // Optional chaining for guideCancelContactBtn

  // Functions to open modals
  function openGuidePasswordModal() {
      document.getElementById('guide-password-confirm-modal').classList.add('show');
      modalOverlay.classList.add('show');
  }

  function openGuideChangeEmailModal() {
      document.getElementById('guide-change-email-modal').classList.add('show');
      modalOverlay.classList.add('show');
  }

  function openGuideChangePasswordModal() {
      document.getElementById('guide-change-password-modal').classList.add('show');
      modalOverlay.classList.add('show');
  }

  function openGuideChangeContactModal() {
      document.getElementById('guide-change-contact-modal').classList.add('show');
      modalOverlay.classList.add('show');
  }

  // Function to close all modals and overlay
  function closeGuideModal() {
      document.querySelectorAll('.modal.show').forEach(modal => modal.classList.remove('show'));
      modalOverlay.classList.remove('show');
      document.getElementById('guide-confirm-password-input').value = ''; // Reset password input
  }
});