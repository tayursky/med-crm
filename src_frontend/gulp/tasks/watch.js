module.exports = function () {
  $.gulp.task('watch', function () {
    $.gulp.watch($.path.src.stylus, $.gulp.series('stylus'));
  });
};
