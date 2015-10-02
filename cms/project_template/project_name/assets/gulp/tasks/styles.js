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
import { config } from './_config';

// - PostCSS - Local documentation for these @ assets/scss/postcss.scss
import assets from 'postcss-assets';
import at2x from 'postcss-at2x';
import autoPrefixer from 'autoprefixer';
import enter from 'postcss-pseudo-class-enter';
import fakeId from 'postcss-fakeid';
import flexbugFixes from 'postcss-flexbugs-fixes';
import propertyLookup from 'postcss-property-lookup';
import willChange from 'postcss-will-change';

const assetsConfig = {
  basePath: 'testing/static/',
  baseUrl: '/static/',
  loadPaths: ['img/', 'svg/']
};

const autoprefixerBrowsers = [
  'last 2 versions',
  'ie >= 9'
];

const postCSSProcessors = [
  // Alphabetical
  assets(assetsConfig),
  at2x,
  enter,
  fakeId,
  propertyLookup,
  willChange,

  // Autoprefixer always 2nd last as the other plugins might add code that
  // needs to be prefixed
  autoPrefixer(autoprefixerBrowsers),

  // Flexbugs always last as it might need to do something the browser
  // prefixed declarations
  flexbugFixes
];

const sassConfig = {
  precision: 10,
  stats: true,
  includePaths: ['node_modules/normalize.scss/'],
  outputStyle: 'expanded'
};

export function styles() {
  return gulp.src(config.sass.src)
    // Initialise source maps
    .pipe($.sourcemaps.init())

    // Process our SCSS to CSS
    .pipe($.sass(sassConfig).on('error', $.sass.logError))

    // PostCSS
    .pipe($.postcss(postCSSProcessors))

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

export function stylesBuild() {
  return gulp.src(config.sass.src)
    .pipe($.sass(sassConfig).on('error', $.sass.logError))
    .pipe($.postcss(postCSSProcessors))
    .pipe($.pxtorem())
    .pipe(gulp.dest(config.css.dist))
}
