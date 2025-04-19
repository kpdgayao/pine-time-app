import { format, formatDistanceToNow, isBefore, parseISO } from 'date-fns';

export function formatDate(dateStr: string): string {
  try {
    return format(parseISO(dateStr), 'PPpp');
  } catch {
    return dateStr;
  }
}

export function formatRelativeTime(dateStr: string): string {
  try {
    return formatDistanceToNow(parseISO(dateStr), { addSuffix: true });
  } catch {
    return dateStr;
  }
}

export function isPast(dateStr: string): boolean {
  try {
    return isBefore(parseISO(dateStr), new Date());
  } catch {
    return false;
  }
}
