/*****************************************************************************/
/* Imports */
/*****************************************************************************/
// - Main
import gulp from 'gulp';
import runSequence from 'run-sequence';
import del from 'del';

// - Gulp modules
import gulpLoadPlugins from 'gulp-load-plugins';
const $ = gulpLoadPlugins();

// - Gulp tasks
import {bower, files} from './{{ project_name }}/assets/gulp/tasks/bower';
import images from './{{ project_name }}/assets/gulp/tasks/images';
import scripts from './{{ project_name }}/assets/gulp/tasks/scripts';
import serve from './{{ project_name }}/assets/gulp/tasks/serve';
import styles from './{{ project_name }}/assets/gulp/tasks/styles';

// - Browser sync
import browserSync from 'browser-sync';
export const bs = browserSync.create();
const reload = bs.reload;

/*****************************************************************************/
/* Tasks */
/*****************************************************************************/
// - Images
gulp.task('images', images);

// - SCSS/CSS Styles
gulp.task('styles', styles);

// - JS Scripts
gulp.task('scripts', scripts);

// - Browser sync
gulp.task('serve', serve);

// - Default task to use when deving
gulp.task('default', (cb) => {
  return runSequence('styles', 'scripts', 'serve', cb);
});
