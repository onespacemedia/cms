/*****************************************************************************/
/* Imports */
/*****************************************************************************/
// - Main
import gulp from 'gulp';

// - Gulp modules
import gulpLoadPlugins from 'gulp-load-plugins';
const $ = gulpLoadPlugins();

// - Browser Sync
import browserSync from 'browser-sync';
const reload = browserSync.reload;

// - Project config
import config from './_config';

// - PostCSS
import assets from 'postcss-assets';
import at2x from 'postcss-at2x';
import autoPrefixer from 'autoprefixer';
import easings from 'postcss-easings';
import enter from 'postcss-pseudo-class-enter';
import fakeId from 'postcss-fakeid';
import flexbugFixes from 'postcss-flexbugs-fixes';
import propertyLookup from 'postcss-property-lookup';
import quantityQueries from 'postcss-quantity-queries';
import willChange from 'postcss-will-change';

export default () => {
  const assetsConfig = {
    basePath: 'testing/static/',
    baseUrl: '/static/',
    loadPaths: ['img/', 'svg/']
  };

  const autoprefixerBrowsers = [
    'last 2 versions',
    'ie >= 9'
  ];

  const postCSSPRocessors = [
    assets(assetsConfig),
    at2x,
    easings,
    enter,
    fakeId,
    quantityQueries,
    willChange,
    propertyLookup,
    autoPrefixer(autoprefixerBrowsers),
    flexbugFixes
  ];

  return gulp.src(config.sass.src)
    // Initialise source maps
    .pipe($.sourcemaps.init())

    // Process our SCSS to CSS
    .pipe($.sass({
      precision: 10,
      stats: true,
      includePaths: ['node_modules/normalize.scss/'],
      outputStyle: 'expanded'
    }).on('error', $.sass.logError))

    // PostCSS
    .pipe($.postcss(postCSSPRocessors))

    // Convert viable px units to REM
    .pipe($.pxtorem())

    // Write our source map, the root is needed for Django funnyness
    .pipe($.sourcemaps.write('./', {
      includeContent: false,
      sourceRoot: () => {
        return '../../static'
      }
    }))

    // Place our CSS in the location we link to
    .pipe(gulp.dest(config.css.dist))

    // Stream the changes to Browser Sync
    .pipe(browserSync.stream({match: '**/*.css'}))

    // Spit out the size to the console
    .pipe($.size({title: 'styles'}));
}
