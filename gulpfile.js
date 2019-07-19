'use strict';

var gulp  = require('gulp');
var clean = require('gulp-clean');
var sass  = require('gulp-sass');

gulp.task('sass:main', function () {
  return gulp.src('./spritesanddice/static/scss/main.scss')
    .pipe(sass().on('error', sass.logError))
    .pipe(gulp.dest('./spritesanddice/static/css'));
});

gulp.task('sass:admin', function () {
  return gulp.src('./spritesanddice/static/scss/admin.scss')
    .pipe(sass().on('error', sass.logError))
    .pipe(gulp.dest('./spritesanddice/static/css'));
});

gulp.task('watch', function () {
  gulp.watch('./spritesanddice/static/scss/**/*.*', gulp.series('sass:main'));
  gulp.watch('./spritesanddice/static/scss/**/*.*', gulp.series('sass:admin'));
});
