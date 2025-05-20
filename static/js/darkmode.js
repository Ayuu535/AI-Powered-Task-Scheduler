// Dark mode toggle functionality
document.addEventListener('DOMContentLoaded', () => {
    const darkModeToggle = document.getElementById('darkModeToggle');
    const themeIcon = document.getElementById('themeIcon');
    
    if (!darkModeToggle) return;
    
    // Check for saved theme preference or use user's system preference
    const prefersDarkScheme = window.matchMedia('(prefers-color-scheme: dark)');
    const savedTheme = localStorage.getItem('theme');
    
    // If user has a saved preference, use that
    if (savedTheme) {
        document.documentElement.setAttribute('data-theme', savedTheme);
        darkModeToggle.checked = savedTheme === 'dark';
        updateThemeIcon(savedTheme === 'dark');
    }
    // Otherwise, use system preference
    else if (prefersDarkScheme.matches) {
        document.documentElement.setAttribute('data-theme', 'dark');
        darkModeToggle.checked = true;
        updateThemeIcon(true);
    }
    
    // Listen for toggle changes
    darkModeToggle.addEventListener('change', () => {
        const theme = darkModeToggle.checked ? 'dark' : 'light';
        document.documentElement.setAttribute('data-theme', theme);
        localStorage.setItem('theme', theme);
        updateThemeIcon(darkModeToggle.checked);
        
        // Announce theme change to screen readers
        const announcement = document.createElement('div');
        announcement.setAttribute('aria-live', 'polite');
        announcement.setAttribute('class', 'sr-only');
        announcement.textContent = `Theme switched to ${theme} mode`;
        document.body.appendChild(announcement);
        
        // Remove announcement after it's read
        setTimeout(() => {
            document.body.removeChild(announcement);
        }, 3000);
    });
    
    // Update theme icon based on current theme
    function updateThemeIcon(isDark) {
        if (themeIcon) {
            if (isDark) {
                themeIcon.classList.remove('bi-sun');
                themeIcon.classList.add('bi-moon-stars');
            } else {
                themeIcon.classList.remove('bi-moon-stars');
                themeIcon.classList.add('bi-sun');
            }
        }
    }
    
    // Also listen for system preference changes
    prefersDarkScheme.addEventListener('change', (e) => {
        // Only update if user hasn't set a preference
        if (!localStorage.getItem('theme')) {
            const theme = e.matches ? 'dark' : 'light';
            document.documentElement.setAttribute('data-theme', theme);
            darkModeToggle.checked = e.matches;
            updateThemeIcon(e.matches);
        }
    });
});
