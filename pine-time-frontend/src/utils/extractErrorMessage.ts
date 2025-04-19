export const extractErrorMessage = (error: any): string => {
  let message = 'Operation failed.';
  const data = error.response?.data;
  if (typeof data === 'string') message = data;
  else if (Array.isArray(data)) message = data.map((e: any) => e.msg || JSON.stringify(e)).join(', ');
  else if (typeof data === 'object' && data !== null) message = data.detail || data.msg || JSON.stringify(data);
  return message;
};
