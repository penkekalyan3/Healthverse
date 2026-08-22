// HealthVerse client-side SPA page initializer and controller
document.addEventListener("DOMContentLoaded", () => {
    const userId = localStorage.getItem('hv_user_id');
    const path = window.location.pathname;

    // Helper to display flash messages
    function showFlash(message, category = 'error', targetElement = null) {
        // Remove existing flash messages
        document.querySelectorAll('.flash-message').forEach(el => el.remove());

        const flashDiv = document.createElement("div");
        flashDiv.className = `flash-message ${category}`;
        flashDiv.style.background = category === 'success' ? 'rgba(124, 252, 0, 0.2)' : 'rgba(255, 0, 0, 0.2)';
        flashDiv.style.border = category === 'success' ? '1px solid rgba(124, 252, 0, 0.4)' : '1px solid rgba(255, 0, 0, 0.4)';
        flashDiv.style.borderRadius = '8px';
        flashDiv.style.color = 'white';
        flashDiv.style.padding = '10px';
        flashDiv.style.marginBottom = '15px';
        flashDiv.style.fontSize = '14px';
        flashDiv.style.textAlign = 'center';
        flashDiv.style.width = '100%';
        flashDiv.textContent = message;

        if (targetElement) {
            targetElement.prepend(flashDiv);
        } else {
            const form = document.querySelector('form');
            if (form) form.parentNode.insertBefore(flashDiv, form);
        }
    }

    // Common Nav bar setup (Logout binding)
    const logoutBtn = document.querySelector('nav ul li a[href*="logout"]');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', (e) => {
            e.preventDefault();
            localStorage.removeItem('hv_user_id');
            localStorage.removeItem('hv_fullname');
            window.location.href = 'index.html';
        });
    }

    // ==========================================
    // LOGIN PAGE
    // ==========================================
    if (path.endsWith('login.html')) {
        const form = document.querySelector('form');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                const email = form.querySelector('input[name="email"]').value;
                const password = form.querySelector('input[name="password"]').value;

                const user = HV_DB.authenticate(email, password);
                if (user) {
                    localStorage.setItem('hv_user_id', user.id);
                    localStorage.setItem('hv_fullname', user.fullname);
                    window.location.href = 'dashboard.html';
                } else {
                    showFlash("Invalid email or password.", "error");
                }
            });
        }
    }

    // ==========================================
    // REGISTER PAGE
    // ==========================================
    if (path.endsWith('register.html')) {
        const form = document.querySelector('form');
        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                const fullname = form.querySelector('input[name="fullname"]').value;
                const email = form.querySelector('input[name="email"]').value;
                const password = form.querySelector('input[name="password"]').value;

                const userId = HV_DB.createUser(fullname, email, password);
                if (userId) {
                    // Set up temporary local storage session to show success on login page
                    localStorage.setItem('hv_reg_success', 'Account created successfully! Please login.');
                    window.location.href = 'login.html';
                } else {
                    showFlash("An account with that email already exists.", "error");
                }
            });
        }
    }

    // Show registration success message if it was set
    if (path.endsWith('login.html')) {
        const successMsg = localStorage.getItem('hv_reg_success');
        if (successMsg) {
            showFlash(successMsg, 'success');
            localStorage.removeItem('hv_reg_success');
        }
    }

    // ==========================================
    // DASHBOARD PAGE
    // ==========================================
    if (path.endsWith('dashboard.html')) {
        const welcomeHeader = document.querySelector('.welcome h1');
        if (welcomeHeader) {
            const fullname = localStorage.getItem('hv_fullname') || 'User';
            welcomeHeader.innerHTML = `Welcome to HealthVerse, ${fullname} 👋`;
        }
    }

    // ==========================================
    // PROFILE PAGE
    // ==========================================
    if (path.endsWith('profile.html')) {
        const form = document.querySelector('form');
        const profile = HV_DB.getProfile(userId);
        const users = HV_DB.getUsers();
        const currentUser = users.find(u => u.id === userId);

        if (form && currentUser) {
            // Populate fields
            form.querySelector('input[name="fullname"]').value = currentUser.fullname;
            form.querySelector('input[name="email"]').value = currentUser.email;

            if (profile) {
                form.querySelector('input[name="age"]').value = profile.age || '';
                form.querySelector('select[name="gender"]').value = profile.gender || 'Female';
                form.querySelector('input[name="height"]').value = profile.height || '';
                form.querySelector('input[name="weight"]').value = profile.weight || '';
                form.querySelector('select[name="goal"]').value = profile.goal || 'Weight Loss';
                form.querySelector('select[name="activity_level"]').value = profile.activity_level || 'Beginner';
            }

            form.addEventListener('submit', (e) => {
                e.preventDefault();
                const fullname = form.querySelector('input[name="fullname"]').value;
                const age = parseInt(form.querySelector('input[name="age"]').value);
                const gender = form.querySelector('select[name="gender"]').value;
                const height = parseFloat(form.querySelector('input[name="height"]').value);
                const weight = parseFloat(form.querySelector('input[name="weight"]').value);
                const goal = form.querySelector('select[name="goal"]').value;
                const activityLevel = form.querySelector('select[name="activity_level"]').value;

                // Update users list fullname
                const allUsers = HV_DB.getUsers();
                const uIndex = allUsers.findIndex(u => u.id === userId);
                if (uIndex !== -1) {
                    allUsers[uIndex].fullname = fullname;
                    localStorage.setItem('hv_users', JSON.stringify(allUsers));
                    localStorage.setItem('hv_fullname', fullname);
                }

                // Save profile details
                HV_DB.saveProfile(userId, age, gender, height, weight, goal, activityLevel);
                showFlash("Profile updated successfully!", "success");
            });
        }
    }

    // ==========================================
    // BMI CALCULATOR PAGE
    // ==========================================
    if (path.endsWith('bmi.html')) {
        const form = document.querySelector('form');
        const profile = HV_DB.getProfile(userId);
        
        if (form) {
            // Pre-fill inputs with profile details if available
            if (profile) {
                form.querySelector('input[name="height"]').value = profile.height || '';
                form.querySelector('input[name="weight"]').value = profile.weight || '';
            }

            form.addEventListener('submit', (e) => {
                e.preventDefault();
                const height = parseFloat(form.querySelector('input[name="height"]').value);
                const weight = parseFloat(form.querySelector('input[name="weight"]').value);

                if (isNaN(height) || isNaN(weight) || height <= 0 || weight <= 0) {
                    showFlash("Please enter valid height and weight values.", "error");
                    return;
                }

                // BMI formula: weight (kg) / [height (m)]^2
                const heightM = height / 100;
                const bmi = weight / (heightM * heightM);
                
                let category = "Normal weight";
                if (bmi < 18.5) category = "Underweight";
                else if (bmi >= 25 && bmi < 30) category = "Overweight";
                else if (bmi >= 30) category = "Obese";

                HV_DB.saveBmi(userId, height, weight, bmi, category);

                // Update results UI
                document.querySelector('.result p').textContent = bmi.toFixed(2);
                document.querySelector('.result span').textContent = `Category: ${category}`;
                showFlash("BMI calculated and saved to history!", "success");
            });
        }
    }

    // ==========================================
    // PROGRESS TRACKER PAGE
    // ==========================================
    if (path.endsWith('progress.html')) {
        const form = document.querySelector('form');
        const profile = HV_DB.getProfile(userId);
        const latestProgress = HV_DB.getLatestProgress(userId);
        const latestBmi = HV_DB.getLatestBmi(userId);

        // Populate display panels
        const weightEl = document.querySelector('.metrics .card:nth-child(1) h3');
        const caloriesEl = document.querySelector('.metrics .card:nth-child(2) h3');
        const waterEl = document.querySelector('.metrics .card:nth-child(3) h3');
        const exerciseEl = document.querySelector('.metrics .card:nth-child(4) h3');
        const sleepEl = document.querySelector('.metrics .card:nth-child(5) h3');

        if (weightEl) {
            weightEl.textContent = latestBmi ? `${latestBmi.weight} kg` : (profile ? `${profile.weight} kg` : '-- kg');
        }
        if (latestProgress) {
            if (caloriesEl) caloriesEl.textContent = `${latestProgress.calories} kcal`;
            if (waterEl) waterEl.textContent = `${latestProgress.water} L`;
            if (exerciseEl) exerciseEl.textContent = `${latestProgress.exercise} Min`;
            if (sleepEl) sleepEl.textContent = `${latestProgress.sleep} Hours`;
        }

        if (form) {
            form.addEventListener('submit', (e) => {
                e.preventDefault();
                const water = parseFloat(form.querySelector('input[name="water"]').value);
                const calories = parseFloat(form.querySelector('input[name="calories"]').value);
                const exercise = parseFloat(form.querySelector('input[name="exercise"]').value);
                const sleep = parseFloat(form.querySelector('input[name="sleep"]').value);

                HV_DB.saveProgress(userId, water, calories, exercise, sleep);
                showFlash("Daily progress logged successfully!", "success");

                // Update UI display directly
                if (caloriesEl) caloriesEl.textContent = `${calories} kcal`;
                if (waterEl) waterEl.textContent = `${water} L`;
                if (exerciseEl) exerciseEl.textContent = `${exercise} Min`;
                if (sleepEl) sleepEl.textContent = `${sleep} Hours`;
            });
        }
    }

    // ==========================================
    // HEALTH REPORTS PAGE
    // ==========================================
    if (path.endsWith('reports.html')) {
        const profile = HV_DB.getProfile(userId);
        const latestProgress = HV_DB.getLatestProgress(userId);
        const latestBmi = HV_DB.getLatestBmi(userId);
        const bmiHistory = HV_DB.getBmiHistory(userId);

        // Update top summaries
        const bmiValEl = document.querySelector('.stats .card:nth-child(1) h3');
        const bmiCatEl = document.querySelector('.stats .card:nth-child(1) p');
        const weightSummaryEl = document.querySelector('.stats .card:nth-child(2) h3');
        const waterSummaryEl = document.querySelector('.stats .card:nth-child(3) h3');
        const caloriesSummaryEl = document.querySelector('.stats .card:nth-child(4) h3');
        const sleepSummaryEl = document.querySelector('.stats .card:nth-child(5) h3');
        const exerciseSummaryEl = document.querySelector('.stats .card:nth-child(6) h3');

        if (latestBmi) {
            if (bmiValEl) bmiValEl.textContent = latestBmi.bmi.toFixed(2);
            if (bmiCatEl) bmiCatEl.textContent = latestBmi.category;
            if (weightSummaryEl) weightSummaryEl.textContent = `${latestBmi.weight} kg`;
        } else if (profile) {
            if (weightSummaryEl) weightSummaryEl.textContent = `${profile.weight} kg`;
        }

        if (latestProgress) {
            if (waterSummaryEl) waterSummaryEl.textContent = `${latestProgress.water} L`;
            if (caloriesSummaryEl) caloriesSummaryEl.textContent = `${latestProgress.calories} kcal`;
            if (sleepSummaryEl) sleepSummaryEl.textContent = `${latestProgress.sleep} hrs`;
            if (exerciseSummaryEl) exerciseSummaryEl.textContent = `${latestProgress.exercise} Min`;
        }

        // Update profile summaries
        const profileGrid = document.querySelector('.profile-summary .grid');
        if (profileGrid) {
            profileGrid.innerHTML = `
                <div><strong>Age:</strong> ${profile ? profile.age : '--'}</div>
                <div><strong>Gender:</strong> ${profile ? profile.gender : '--'}</div>
                <div><strong>Goal:</strong> ${profile ? profile.goal : '--'}</div>
                <div><strong>Height:</strong> ${profile ? profile.height : '--'} cm</div>
                <div><strong>Weight:</strong> ${profile ? profile.weight : '--'} kg</div>
                <div><strong>Activity Level:</strong> ${profile ? profile.activity_level : '--'}</div>
            `;
        }

        // Render BMI History Table
        const tableBody = document.querySelector('table tbody');
        if (tableBody) {
            tableBody.innerHTML = '';
            if (bmiHistory.length === 0) {
                tableBody.innerHTML = `
                    <tr>
                        <td colspan="5" style="padding: 15px; text-align: center; color: rgba(255,255,255,0.6);">
                            No BMI measurements logged yet.
                        </td>
                    </tr>
                `;
            } else {
                bmiHistory.forEach(record => {
                    const row = document.createElement('tr');
                    row.style.borderBottom = '1px solid rgba(255,255,255,0.08)';
                    row.innerHTML = `
                        <td style="padding: 10px;">${new Date(record.date).toLocaleString()}</td>
                        <td style="padding: 10px;">${record.height} cm</td>
                        <td style="padding: 10px;">${record.weight} kg</td>
                        <td style="padding: 10px;">${record.bmi.toFixed(2)}</td>
                        <td style="padding: 10px;">${record.category}</td>
                    `;
                    tableBody.appendChild(row);
                });
            }
        }

        // Handle client-side PDF printing
        const downloadBtn = document.querySelector('a[href*="download"]');
        if (downloadBtn) {
            downloadBtn.removeAttribute('href');
            downloadBtn.style.cursor = 'pointer';
            downloadBtn.addEventListener('click', (e) => {
                e.preventDefault();
                window.print();
            });
        }
    }
});
