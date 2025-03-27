import { getInitials } from './helpers';

describe('getInitials', () => {
  it('should return initials from name', () => {
    expect(getInitials('John Doe', null)).toBe('JD');
  });

  it('should return initials from name with meta', () => {
    expect(getInitials('John Doe (John)', null)).toBe('JD');
  });

  it('should return the first letter from email', () => {
    expect(getInitials(null, 'sam@example.com')).toBe('S');
  });

  it('should return "?" when neither name nor email is provided', () => {
    expect(getInitials(null, null)).toBe('?');
  });
});
