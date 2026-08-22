// LocalStorage Database for HealthVerse (GitHub Pages client-side mode)
const HV_DB = {
    getUsers: () => JSON.parse(localStorage.getItem('hv_users') || '[]'),
    getProfiles: () => JSON.parse(localStorage.getItem('hv_profiles') || '{}'),
    getBmiLogs: () => JSON.parse(localStorage.getItem('hv_bmi_logs') || '[]'),
    getProgressLogs: () => JSON.parse(localStorage.getItem('hv_progress_logs') || '[]'),
    getYogaSessions: () => JSON.parse(localStorage.getItem('hv_yoga_sessions') || '[]'),
    getBadges: () => JSON.parse(localStorage.getItem('hv_user_badges') || '[]'),

    createUser: (fullname, email, password) => {
        const users = HV_DB.getUsers();
        if (users.find(u => u.email.toLowerCase() === email.toLowerCase())) return false;
        const userId = 'user_' + Date.now();
        users.push({ id: userId, fullname, email, password });
        localStorage.setItem('hv_users', JSON.stringify(users));
        return userId;
    },

    authenticate: (email, password) => {
        const users = HV_DB.getUsers();
        const user = users.find(u => u.email.toLowerCase() === email.toLowerCase() && u.password === password);
        return user ? { id: user.id, fullname: user.fullname } : null;
    },

    getProfile: (userId) => {
        const profiles = HV_DB.getProfiles();
        return profiles[userId] || null;
    },

    saveProfile: (userId, age, gender, height, weight, goal, activityLevel) => {
        const profiles = HV_DB.getProfiles();
        profiles[userId] = { age, gender, height, weight, goal, activity_level: activityLevel };
        localStorage.setItem('hv_profiles', JSON.stringify(profiles));
    },

    saveBmi: (userId, height, weight, bmi, category) => {
        const logs = HV_DB.getBmiLogs();
        logs.unshift({ 
            id: 'bmi_' + Date.now(), 
            user_id: userId, 
            height: parseFloat(height), 
            weight: parseFloat(weight), 
            bmi: parseFloat(bmi), 
            category, 
            date: new Date().toISOString() 
        });
        localStorage.setItem('hv_bmi_logs', JSON.stringify(logs));
    },

    getBmiHistory: (userId) => {
        return HV_DB.getBmiLogs().filter(log => log.user_id === userId);
    },

    getLatestBmi: (userId) => {
        const logs = HV_DB.getBmiHistory(userId);
        return logs.length > 0 ? logs[0] : null;
    },

    saveProgress: (userId, water, calories, exercise, sleep) => {
        const logs = HV_DB.getProgressLogs();
        logs.unshift({ 
            id: 'prog_' + Date.now(), 
            user_id: userId, 
            water: parseFloat(water), 
            calories: parseFloat(calories), 
            exercise: parseFloat(exercise), 
            sleep: parseFloat(sleep), 
            date: new Date().toISOString() 
        });
        localStorage.setItem('hv_progress_logs', JSON.stringify(logs));
    },

    getLatestProgress: (userId) => {
        const logs = HV_DB.getProgressLogs().filter(log => log.user_id === userId);
        return logs.length > 0 ? logs[0] : null;
    },

    saveYogaSession: (userId, sessionDate, startTime, endTime, duration, calories, completedPoses, status, avgBpm = null, maxBpm = null) => {
        const sessions = HV_DB.getYogaSessions();
        sessions.unshift({
            id: 'yoga_' + Date.now(),
            user_id: userId,
            session_date: sessionDate,
            start_time: startTime,
            end_time: endTime,
            duration: parseInt(duration),
            calories: parseInt(calories),
            completed_poses: parseInt(completedPoses),
            status,
            avg_bpm: avgBpm,
            max_bpm: maxBpm
        });
        localStorage.setItem('hv_yoga_sessions', JSON.stringify(sessions));
    },

    getYogaSessions: (userId) => {
        const sessions = JSON.parse(localStorage.getItem('hv_yoga_sessions') || '[]');
        return sessions.filter(s => s.user_id === userId);
    },

    awardBadgeIfNew: (userId, badgeName) => {
        const badges = HV_DB.getBadges();
        const existing = badges.find(b => b.user_id === userId && b.badge_name === badgeName);
        if (existing) return false;
        badges.push({ user_id: userId, badge_name: badgeName, awarded_date: new Date().toISOString() });
        localStorage.setItem('hv_user_badges', JSON.stringify(badges));
        return true;
    },

    getUserBadges: (userId) => {
        return HV_DB.getBadges().filter(b => b.user_id === userId);
    },

    getStreakDays: (userId) => {
        const sessions = HV_DB.getYogaSessions(userId).filter(s => s.status === 'Completed');
        if (sessions.length === 0) return 0;
        
        // Calculate consecutive active days
        const dates = [...new Set(sessions.map(s => s.session_date.split(' ')[0]))]
            .map(d => new Date(d))
            .sort((a, b) => b - a);
            
        if (dates.length === 0) return 0;
        
        const today = new Date();
        today.setHours(0,0,0,0);
        const yesterday = new Date(today);
        yesterday.setDate(yesterday.getDate() - 1);
        
        const latestDate = new Date(dates[0]);
        latestDate.setHours(0,0,0,0);
        
        if (latestDate.getTime() !== today.getTime() && latestDate.getTime() !== yesterday.getTime()) {
            return 0;
        }
        
        let streak = 1;
        let currentDate = latestDate;
        
        for (let i = 1; i < dates.length; i++) {
            const nextDate = new Date(dates[i]);
            nextDate.setHours(0,0,0,0);
            
            const diffTime = Math.abs(currentDate - nextDate);
            const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24));
            
            if (diffDays === 1) {
                streak++;
                currentDate = nextDate;
            } else if (diffDays > 1) {
                break;
            }
        }
        return streak;
    }
};
