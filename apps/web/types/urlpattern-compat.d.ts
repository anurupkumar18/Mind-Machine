/** Compatibility names required by Next.js until TypeScript's DOM lib ships them. */
declare global {
  type URLPatternInput = URLPatternInit | string;

  interface URLPatternOptions {
    ignoreCase?: boolean;
  }
}

export {};
