export const getInitials = (name: string | null, email: string | null) => {
  console.log('name', name, email);
  if (name) {
    const cleanName = name.replace(/\(.*?\)/, '').trim();

    return cleanName
      .split(' ')
      .map((n) => n[0])
      .join('')
      .toUpperCase();
  }

  if (email) {
    return email[0]?.toUpperCase() ?? '?';
  }

  return '?';
};
