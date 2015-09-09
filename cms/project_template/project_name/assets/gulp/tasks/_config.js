// Paths from root of Gulpfile
const srcFolder = './{{ project_name }}/assets';
const distFolder = './{{ project_name }}/static';
const templateFolder = './{{ project_name }}/templates';

export default {
  bower: {
    path: 'bower_components'
  },
  css: {
    dist: `${distFolder}/css`,
    src: `${srcFolder}/scss`
  },
  images: {
    dist: `${distFolder}/images`,
    src: [
      `${srcFolder}/img/**/*`
    ]
  },
  js: {
    dist: `${distFolder}/js`,
    src: [
      `${srcFolder}/*.js`,
      `${srcFolder}/**/*.js`
    ]
  },
  html: {
    dist: templateFolder,
    src: [
      `${templateFolder}/*.html`,
      `${templateFolder}/**/*.html`
    ]
  },
  sass: {
    src: [
      `${srcFolder}/scss/*.scss`,
      `${srcFolder}/scss/**/*.scss`
    ]
  },
  watchify: {
    fileIn: `${srcFolder}/js/main.js`,
    fileOut: `app.js`,
    srcFolder: `${srcFolder}/js`,
    distFolder: `${distFolder}/js`
  }
};
