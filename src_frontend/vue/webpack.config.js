'use strict';

const environment = (process.env.NODE_ENV && process.env.NODE_ENV.trim() === 'development');

if (environment) {
    module.exports = require('./config/webpack.config.dev');
} else {
    module.exports = require('./config/webpack.config.prod');
}