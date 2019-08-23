'use strict';

var gulp  = require('gulp');
var clean = require('gulp-clean');
var sass  = require('gulp-sass');

gulp.task('sass:main', function () {
	return gulp.src('./spritesanddice/static/scss/main/main.scss')
		.pipe(sass().on('error', sass.logError))
		.pipe(gulp.dest('./spritesanddice/static/css'));
});

gulp.task('sass:admin', function () {
return gulp.src('./spritesanddice/static/scss/admin/admin.scss')
	.pipe(sass().on('error', sass.logError))
	.pipe(gulp.dest('./spritesanddice/static/css'));
});

gulp.task('sass:userbar', function () {
	return gulp.src('./spritesanddice/static/scss/userbar.scss')
		.pipe(sass().on('error', sass.logError))
		.pipe(gulp.dest('./spritesanddice/static/wagtailadmin/css/'));
});


gulp.task('watch', function () {
	gulp.watch('./spritesanddice/static/scss/userbar.scss',  gulp.series('sass:userbar'));
	gulp.watch('./spritesanddice/static/scss/**/*.scss', gulp.series('sass:main'));
	gulp.watch('./spritesanddice/static/scss/**/*.scss', gulp.series('sass:admin'));
});
