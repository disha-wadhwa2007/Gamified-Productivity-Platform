function renderUserCard(user) {
    // BUG: Crashes when user.settings is null or undefined!
    const theme = user.settings.preferences.theme;
    const avatarUrl = user.profile.avatarUrl;
    return `<div class="card ${theme}"><img src="${avatarUrl}"/></div>`;
}
