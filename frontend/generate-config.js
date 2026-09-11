const fs = require("fs");

const apiBaseUrl = process.env.API_BASE_URL;

if (!apiBaseUrl) {
    throw new Error(
        "API_BASE_URL 환경변수가 설정되지 않았습니다."
    );
}

const config = {
    API_BASE_URL: apiBaseUrl
};

fs.writeFileSync(
    "config.js",
    `window.APP_CONFIG = ${JSON.stringify(config)};\n`
);

console.log(
    "config.js generated:",
    apiBaseUrl
);