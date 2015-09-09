import gulp from 'gulp';
import gulpLoadPlugins from 'gulp-load-plugins';
import browserSync from 'browser-sync';
import {bs} from '../../../../Gulpfile.babel';
import config from './_config';

const $ = gulpLoadPlugins();
const reload = browserSync.reload;

export function bower() {
  return $.bower()
    .pipe(gulp.dest(config.bower.path));
}

export function files() {
  // Move the Vendor JS files
  gulp.src([
    'bower_components/fastclick/lib/fastclick.js',
    'bower_components/jquery/dist/jquery.js',
    'bower_components/jquery-placeholder/jquery.placeholder.js',
    'bower_components/jquery.cookie/jquery.cookie.js',
    'bower_components/modernizr/modernizr.js',
    'bower_components/modernizr/modernizr.js',
  ])
    .pipe(gulp.dest(`${config.watchify.srcFolder}/vendor/`));

  // Move the Foundation JS files
  gulp.src('bower_components/foundation/js/foundation/*')
    .pipe(gulp.dest(`${config.watchify.srcFolder}/vendor/foundation/`));

  // Move the Foundation CSS files
  gulp.src([
    'bower_components/foundation/scss/normalize.scss',
    'bower_components/foundation/scss/**/*',
    '!bower_components/foundation/scss/foundation.scss',
  ])
    .pipe(gulp.dest(`${config.css.src}`));

  // Move base Foundation file and rename it
  gulp.src('bower_components/foundation/scss/foundation.scss')
    .pipe($.rename({
      basename: 'screen'
    }))
    .pipe(gulp.dest(`${config.css.src}`));
}
