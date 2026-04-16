// Standalone cn() utility - no external dependencies required
// This merges class names intelligently, filtering falsy values
type ClassValue = string | number | boolean | undefined | null | ClassValue[];

function clsx(...inputs: ClassValue[]): string {
  return inputs
    .flat(Infinity as 0)
    .filter(Boolean)
    .join(' ');
}

export function cn(...inputs: ClassValue[]): string {
  // Simple implementation: merge class strings and deduplicate
  return clsx(...inputs);
}
