module.exports = function () {
  $.gulp.task('stylus', function () {
    return $.gulp.src('stylus/main.styl')
      .pipe($.gp.sourcemaps.init())
      .pipe($.gp.stylus({
        'include css': true
      }))
      .pipe($.gp.autoprefixer({
        browsers: ['last 10 versions']
      }))
      .on('error', $.gp.notify.onError({
        message: "Error: <%= error.message %>",
        title: "stile"
      }))
      // .pipe($.gp.csso())
      .pipe($.gp.sourcemaps.write())
      .pipe($.gulp.dest('../static'));
  });
};
