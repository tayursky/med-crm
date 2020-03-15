'use strict';

global.$ = {
  gulp: require('gulp'),
  gp: require('gulp-load-plugins')(),
  browserSync: require('browser-sync').create(),
  /* параметры для gulp-autoprefixer */
  autoprefixerList: [
    'Android >= 4.4', 'Chrome >= 45', 'Firefox ESR', 'Explorer >= 10', 'Opera >= 30'
  ],
  path: {
    tasks: [
      './gulp/tasks/stylus',
      './gulp/tasks/watch'
    ],
    src: {
      stylus: 'stylus/**/*.styl',
      html: 'src/*.html',
      js: 'src/**/*.js',
      img: 'src/img/**/*.*',
      fonts: 'src/fonts/**/*.*'
    },
    build: {
      css: '../../static/css/',
      html: '../../static/dist/',
      js: '../../static/dist/js/',
      img: '../../static/dist/img/',
      fonts: '../../static/dist/fonts/'
    },
    clean: '../../static/dist'
  }
};

$.path.tasks.forEach(function (taskPath) {
  require(taskPath)();
});

$.gulp.task('default',
  $.gulp.series(
    $.gulp.parallel('stylus'),
    'watch'
    // gulp.parallel('watch', 'browser-sync')
  )
);
