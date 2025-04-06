export const getInitials = (name: string | null, email: string | null) => {
  if (name && !name.includes('Anonymous')) {
    const cleanName = name.replace(/\(.*?\)/, '').trim();

    return cleanName
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase();
  }

  if (email && !email.includes('guest')) {
    return email[0]?.toUpperCase() ?? '?';
  }

  return '?';
};
