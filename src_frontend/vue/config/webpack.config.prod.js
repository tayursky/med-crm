'use strict';

const webpack = require('webpack');
const merge = require('webpack-merge');
const OptimizeCSSAssetsPlugin = require('optimize-css-assets-webpack-plugin');
const MiniCSSExtractPlugin = require('mini-css-extract-plugin');
const UglifyJsPlugin = require('uglifyjs-webpack-plugin');
const CompressionPlugin = require('compression-webpack-plugin');
const helpers = require('./helpers');
const commonConfig = require('./webpack.config.common');
const isProd = process.env.NODE_ENV === 'production';
const environment = isProd ? require('./env/prod.env') : require('./env/staging.env');


const webpackConfig = merge(commonConfig, {
  mode: 'production',
  devtool: 'cheap-module-source-map',
  output: {
    publicPath: '/',
    path: helpers.root('../../static/dist'),
    filename: 'js/[name].bundle.js',
    chunkFilename: 'js/[id].chunk.js'
  },
  optimization: {
    runtimeChunk: 'single',
    minimizer: [
      new OptimizeCSSAssetsPlugin({
        cssProcessorPluginOptions: {
          preset: ['default', {discardComments: {removeAll: true}}],
        }
      }),

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
    // splitChunks: {
    //   chunks: 'all',
    //   maxInitialRequests: Infinity,
    //   minSize: 0,
    //   cacheGroups: {
    //     vendor: {
    //       test: /[\\/]node_modules[\\/]/,
    //       name(module) {
    //         const packageName = module.context.match(/[\\/]node_modules[\\/](.*?)([\\/]|$)/)[1];
    //         return `npm.${packageName.replace('@', '')}`;
    //       }
    //     },
    //     styles: {
    //       test: /\.css$/,
    //       name: 'styles',
    //       chunks: 'all',
    //       enforce: true
    //     }
    //   }
    // }
  },
  plugins: [
    new webpack.EnvironmentPlugin(environment),
    new MiniCSSExtractPlugin({
      filename: 'css/[name].[hash].css',
      chunkFilename: 'css/[id].[hash].css'
    }),
    // new CompressionPlugin({
    //   filename: '[path].gz[query]',
    //   algorithm: 'gzip',
    //   test: new RegExp('\\.(js|css)$'),
    //   threshold: 10240,
    //   minRatio: 0.8
    // }),
    new webpack.HashedModuleIdsPlugin()
  ]
});

// if (!isProd) {
  webpackConfig.devtool = 'source-map';

  const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin;
  webpackConfig.plugins.push(new BundleAnalyzerPlugin());
// }

module.exports = webpackConfig;