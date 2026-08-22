/**
 * Yoga Session Workflow Handler - Clean Professional Video Player Edition
 * Manages custom HTML5 video controls, plays the selected pose video fully with its original audio,
 * and shows "Session Completed" upon natural completion of the routine.
 */

// Pose Database Configuration
const YOGA_POSES = [
    {
        name: "Mountain Pose",
        id: "mountain",
        video: "mountain.mp4",
        calorieRate: 2.5
    },
    {
        name: "Tree Pose",
        id: "tree",
        video: "tree.mp4",
        calorieRate: 3.0
    },
    {
        name: "Cobra Pose",
        id: "cobra",
        video: "cobra.mp4",
        calorieRate: 4.0
    },
    {
        name: "Child's Pose",
        id: "child",
        video: "child.mp4",
        calorieRate: 2.0
    },
    {
        name: "Downward Dog",
        id: "downwarddog",
        video: "downward_dog.mp4",
        calorieRate: 4.5
    },
    {
        name: "Sun Salutation",
        id: "sunsalutation",
        video: "sun_salutation.mp4",
        calorieRate: 7.5
    }
];

// Session State
let currentPoseIndex = 0;
let isPlaying = false;
let sessionStartTime = null;

// DOM Elements
const sessionModal = document.getElementById("yoga-session-modal");
const activeView = document.getElementById("active-session-view");
const completionView = document.getElementById("completion-session-view");
const poseName = document.getElementById("pose-name");
const poseVideo = document.getElementById("pose-video");

const playPauseBtn = document.getElementById("play-pause-btn");
const playPauseIcon = document.getElementById("play-pause-icon");
const skipPoseBtn = document.getElementById("skip-pose-btn");
const endSessionBtn = document.getElementById("end-session-btn");
const btnRestartSession = document.getElementById("btn-restart-session");

const timeDisplay = document.getElementById("time-display");
const progressContainer = document.getElementById("progress-container");
const progressFill = document.getElementById("progress-fill");

const muteBtn = document.getElementById("mute-btn");
const muteIcon = document.getElementById("mute-icon");
const volumeSlider = document.getElementById("volume-slider");
const fullscreenBtn = document.getElementById("fullscreen-btn");

// Initialize Session
function initSession(index) {
    currentPoseIndex = index;
    sessionStartTime = new Date();
    
    // UI Resets
    activeView.style.display = "flex";
    completionView.style.display = "none";
    
    loadPose(currentPoseIndex);
}

// Load Pose Video
function loadPose(index) {
    const pose = YOGA_POSES[index];
    if (!pose) return;

    poseName.textContent = pose.name;
    
    // Set video source
    poseVideo.src = `static/assets/yoga_videos/${pose.video}`;
    poseVideo.load();
    
    // Reset video properties
    poseVideo.currentTime = 0;
    poseVideo.muted = false;
    poseVideo.volume = volumeSlider.value;
    updateMuteIcon(poseVideo.volume);

    // Auto play video
    poseVideo.play()
        .then(() => {
            setPlayState(true);
        })
        .catch(err => {
            console.log("Auto play prevented, waiting for user click.", err);
            setPlayState(false);
        });
}

// Control Play / Pause State
function setPlayState(play) {
    isPlaying = play;
    if (play) {
        playPauseIcon.textContent = "⏸";
        playPauseBtn.title = "Pause";
    } else {
        playPauseIcon.textContent = "▶";
        playPauseBtn.title = "Play";
    }
}

function togglePlay() {
    if (poseVideo.paused) {
        poseVideo.play()
            .then(() => setPlayState(true))
            .catch(err => console.error("Play failed:", err));
    } else {
        poseVideo.pause();
        setPlayState(false);
    }
}

// Format Time helper (seconds to MM:SS)
function formatTime(seconds) {
    if (isNaN(seconds) || seconds === Infinity) return "00:00";
    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);
    return `${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
}

// Update time display and progress bar
function updateProgress() {
    const current = poseVideo.currentTime || 0;
    const duration = poseVideo.duration || 0;
    
    timeDisplay.textContent = `${formatTime(current)} / ${formatTime(duration)}`;
    
    if (duration > 0) {
        const percent = (current / duration) * 100;
        progressFill.style.width = `${percent}%`;
    } else {
        progressFill.style.width = "0%";
    }
}

// Scrub video time on progress click
function scrub(e) {
    const rect = progressContainer.getBoundingClientRect();
    const clickX = e.clientX - rect.left;
    const width = rect.width;
    const duration = poseVideo.duration;
    if (duration > 0 && width > 0) {
        const newTime = (clickX / width) * duration;
        poseVideo.currentTime = newTime;
    }
}

// Mute/Unmute
function toggleMute() {
    poseVideo.muted = !poseVideo.muted;
    if (poseVideo.muted) {
        muteIcon.textContent = "🔇";
        muteBtn.title = "Unmute";
    } else {
        updateMuteIcon(poseVideo.volume);
        muteBtn.title = "Mute";
    }
}

// Update Mute Icon based on volume level
function updateMuteIcon(volume) {
    if (volume === 0 || poseVideo.muted) {
        muteIcon.textContent = "🔇";
    } else if (volume < 0.5) {
        muteIcon.textContent = "🔉";
    } else {
        muteIcon.textContent = "🔊";
    }
}

// Fullscreen mode handler
function toggleFullscreen() {
    const container = document.querySelector(".video-player-container");
    if (!document.fullscreenElement) {
        if (container.requestFullscreen) {
            container.requestFullscreen();
        } else if (container.mozRequestFullScreen) { // Firefox
            container.mozRequestFullScreen();
        } else if (container.webkitRequestFullscreen) { // Chrome, Safari and Opera
            container.webkitRequestFullscreen();
        } else if (container.msRequestFullscreen) { // IE/Edge
            container.msRequestFullscreen();
        }
    } else {
        if (document.exitFullscreen) {
            document.exitFullscreen();
        }
    }
}

// Move to next pose in sequence
function moveToNextPose() {
    if (currentPoseIndex < YOGA_POSES.length - 1) {
        currentPoseIndex++;
        loadPose(currentPoseIndex);
    } else {
        endWorkout(true);
    }
}

// End workout (completed naturally or finished sequence)
function endWorkout(completedSuccessfully = false) {
    poseVideo.pause();
    
    if (completedSuccessfully) {
        // Show completion view
        activeView.style.display = "none";
        completionView.style.display = "flex";
        
        // Log workout to SQLite database in the background
        const endTime = new Date();
        const durationSec = Math.round((endTime - sessionStartTime) / 1000);
        const pose = YOGA_POSES[currentPoseIndex];
        const calories = Math.round((durationSec / 60) * (pose ? pose.calorieRate : 3.0));
        
        logWorkoutToSQLite(durationSec, calories, 1, sessionStartTime, endTime);
    } else {
        closeOverlayModal();
    }
}

// Local database logger for GitHub Pages
function logWorkoutToSQLite(durationSec, calories, poses, startDt, endDt) {
    const formatDateISO = (d) => d.toISOString().split('T')[0];
    const formatTimeOnly = (d) => d.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', hour12: true });
    
    const userId = localStorage.getItem('hv_user_id') || 'demo_user';
    const sessionDate = formatDateISO(startDt);
    const startTime = formatTimeOnly(startDt);
    const endTime = formatTimeOnly(endDt);

    // 1. Save yoga session details locally
    HV_DB.saveYogaSession(userId, sessionDate, startTime, endTime, durationSec, calories, poses, "Completed");

    // 2. Add to daily progress trackers automatically
    const minutes = Math.max(1, Math.round(durationSec / 60));
    const latestProgress = HV_DB.getLatestProgress(userId) || { water: 0, sleep: 0 };
    HV_DB.saveProgress(userId, latestProgress.water, calories, minutes, latestProgress.sleep);

    // 3. Award badges
    const newBadges = [];
    const allSessions = HV_DB.getYogaSessions(userId);
    const completedSessions = allSessions.filter(s => s.status === "Completed");

    if (completedSessions.length >= 1) {
        if (HV_DB.awardBadgeIfNew(userId, "First Session")) {
            newBadges.push("First Session");
        }
    }
    if (completedSessions.length >= 10) {
        if (HV_DB.awardBadgeIfNew(userId, "Yoga Master")) {
            newBadges.push("Yoga Master");
        }
    }
    const streakDays = HV_DB.getStreakDays(userId);
    if (streakDays >= 7) {
        if (HV_DB.awardBadgeIfNew(userId, "7 Day Streak")) {
            newBadges.push("7 Day Streak");
        }
    }
    if (streakDays >= 30) {
        if (HV_DB.awardBadgeIfNew(userId, "30 Day Streak")) {
            newBadges.push("30 Day Streak");
        }
    }

    console.log("Workout logged to local storage. Streak:", streakDays, "New badges:", newBadges);
    
    // Update db status message on completion page
    const statusBanner = document.getElementById("db-logging-status");
    if (statusBanner) {
        statusBanner.textContent = "Workout saved successfully to your offline profile!";
        statusBanner.style.background = "rgba(124, 252, 0, 0.2)";
        statusBanner.style.color = "#7CFC00";
    }

    // Display badges if unlocked
    const badgesSection = document.getElementById("badges-unlocked-section");
    const badgesContainer = document.getElementById("badges-unlocked-container");
    if (badgesSection && badgesContainer && newBadges.length > 0) {
        badgesSection.style.display = "block";
        badgesContainer.innerHTML = "";
        newBadges.forEach(badge => {
            const badgeDiv = document.createElement("div");
            badgeDiv.className = "badge-item";
            const icon = badge === "First Session" ? "🥉" : (badge === "Yoga Master" ? "🏆" : "🏅");
            badgeDiv.innerHTML = `<h3>${icon} ${badge}</h3>`;
            badgesContainer.appendChild(badgeDiv);
        });
    }
}

// Close session modal overlay
function closeOverlayModal() {
    sessionModal.style.display = "none";
    poseVideo.pause();
    poseVideo.src = "";
    isPlaying = false;
}

// Event Bindings
document.addEventListener("DOMContentLoaded", () => {
    
    // Play/Pause button
    playPauseBtn.addEventListener("click", togglePlay);
    
    // Skip button (Immediately load and play the next video)
    skipPoseBtn.addEventListener("click", () => {
        moveToNextPose();
    });
    
    // End Session button (Immediately return to dashboard)
    if (endSessionBtn) {
        endSessionBtn.addEventListener("click", () => {
            closeOverlayModal();
        });
    }
    
    // Restart from completion view
    btnRestartSession.addEventListener("click", () => {
        initSession(currentPoseIndex);
    });
    
    // Mute button
    muteBtn.addEventListener("click", toggleMute);
    
    // Volume slider
    volumeSlider.addEventListener("input", (e) => {
        const val = parseFloat(e.target.value);
        poseVideo.volume = val;
        poseVideo.muted = (val === 0);
        updateMuteIcon(val);
    });
    
    // Fullscreen button
    fullscreenBtn.addEventListener("click", toggleFullscreen);
    
    // Progress Bar clicking
    progressContainer.addEventListener("click", scrub);
    
    // Video elements events
    poseVideo.addEventListener("timeupdate", updateProgress);
    poseVideo.addEventListener("loadedmetadata", updateProgress);
    
    // End of video behavior (advance to next pose video naturally)
    poseVideo.addEventListener("ended", () => {
        moveToNextPose();
    });
    
    // Attach trigger listeners to start buttons on the dashboard cards
    const startButtons = document.querySelectorAll(".card button");
    startButtons.forEach((btn, index) => {
        btn.addEventListener("click", (e) => {
            e.preventDefault();
            
            // Show session overlay modal
            sessionModal.style.display = "flex";
            
            // Initialize session for specific pose card clicked
            initSession(index);
        });
    });
});
