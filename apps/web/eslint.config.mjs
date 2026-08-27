import nextVitals from "eslint-config-next/core-web-vitals";

const config = [...nextVitals, { ignores: [".next/**", "types/**/*.d.ts"] }];

export default config;
