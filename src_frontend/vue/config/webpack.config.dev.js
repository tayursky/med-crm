'use strict';

const webpack = require('webpack');
const merge = require('webpack-merge');
const CompressionPlugin = require('compression-webpack-plugin');
const FriendlyErrorsPlugin = require('friendly-errors-webpack-plugin');
const helpers = require('./helpers');
const commonConfig = require('./webpack.config.common');
const environment = require('./env/dev.env');
const UglifyJsPlugin = require('uglifyjs-webpack-plugin');

const webpackConfig = merge(commonConfig, {
  mode: 'development',
  output: {
    publicPath: '/',
    path: helpers.root('../../static/dist'),
    filename: 'js/[name].bundle.js',
    chunkFilename: 'js/[id].chunk.js'
  },
  optimization: {
    minimizer: [
      new UglifyJsPlugin({
        test: /\.js(\?.*)?$/i,
        extractComments: 'all',
        sourceMap: true,
        uglifyOptions: {
          warnings: false,
          parse: {},
          compress: {},
          mangle: true, // Note `mangle.properties` is `false` by default.
          output: null,
          toplevel: false,
          nameCache: null,
          ie8: false,
          keep_fnames: false,
          beautify: false,
          comments: false,
        },
      })
    ],
    runtimeChunk: 'single',
    splitChunks: {
      chunks: 'all'
    }
  },
  plugins: [
    new webpack.EnvironmentPlugin(environment),
    new webpack.HotModuleReplacementPlugin(),
    new FriendlyErrorsPlugin(),
  ],
  devServer: {
    compress: true,
    historyApiFallback: true,
    hot: true,
    open: true,
    overlay: true,
    port: 8000,
    stats: {
      normal: true
    }
  }
});

module.exports = webpackConfig;