/*****************************************************************************/
/* Imports */
/*****************************************************************************/
// - Main
import gulp from 'gulp';
import runSequence from 'run-sequence';

// - Gulp modules
import gulpLoadPlugins from 'gulp-load-plugins';
const $ = gulpLoadPlugins();

// - Gulp tasks
import images from './{{ project_name }}/assets/gulp/tasks/images';
import { scripts, scriptsBuild } from './{{ project_name }}/assets/gulp/tasks/scripts';
import serve from './{{ project_name }}/assets/gulp/tasks/serve';
import { styles, stylesBuild } from './{{ project_name }}/assets/gulp/tasks/styles';

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
gulp.task('stylesBuild', stylesBuild);

// - JS Scripts
gulp.task('scripts', scripts);
gulp.task('scriptsBuild', scriptsBuild);

// - Browser sync
gulp.task('serve', serve);

// - Build
gulp.task('build', (cb) => runSequence('stylesBuild', 'scriptsBuild', cb));

// - Default task to use when deving
gulp.task('default', (cb) => {
  return runSequence('styles', 'scripts', 'serve', cb);
});
