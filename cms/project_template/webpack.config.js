var path = require('path');

var webpack = require('webpack');
var production = process.env.NODE_ENV === 'production';
var ExtractPlugin = require('extract-text-webpack-plugin');

var at2x = require('postcss-at2x');
var autoPrefixer = require('autoprefixer');
var enter = require('postcss-pseudo-class-enter');
var fakeId = require('postcss-fakeid');
var flexbugFixes = require('postcss-flexbugs-fixes');
var propertyLookup = require('postcss-property-lookup');
var pxToRem = require('postcss-pxtorem');
var willChange = require('postcss-will-change');

var plugins = [
  // This plugins optimizes chunks and modules by
  // how much they are used in your app
  new webpack.optimize.OccurenceOrderPlugin(),
  new webpack.HotModuleReplacementPlugin(),
  new webpack.NoErrorsPlugin(),
  new webpack.ProvidePlugin({
    _: 'lodash',
    Vue: 'vue'
  })
];

if (production) {
  plugins = plugins.concat([
    // This plugin looks for similar chunks and files
    // and merges them for better caching by the user
    new webpack.optimize.DedupePlugin(),
    // This plugin prevents Webpack from creating chunks
    // that would be too small to be worth loading separately
    new webpack.optimize.MinChunkSizePlugin({
      minChunkSize: 51200, // ~50kb
    }),
    // This plugin minifies all the Javascript code of the final bundle
    new webpack.optimize.UglifyJsPlugin({
      mangle: true,
      compress: {
        warnings: false, // Suppress uglification warnings
      }
    }),
    new ExtractPlugin('bundle.css'),
    // This plugins defines various variables that we can set to false
    // in production to avoid code related to them from being compiled
    // in our final bundle
    new webpack.DefinePlugin({
      __SERVER__: !production,
      __DEVELOPMENT__: !production,
      __DEVTOOLS__: !production,
      'process.env': {
        BABEL_ENV: JSON.stringify(process.env.NODE_ENV)
      }
    })
  ]);
}

module.exports = {
  debug: !production,

  devtool: production ? false : 'eval',

  context: path.join(__dirname, '{{ project_name }}', 'assets'),

  entry: [
    'webpack/hot/dev-server',
    'webpack-hot-middleware/client',
    './js/index'
  ],

  output: {
    path: path.join(__dirname, '{{ project_name }}', 'static'),
    filename: 'bundle.js',
    chunkFilename: '[name]-[chunkhash].js',
    publicPath: '/static/'
  },

  module: {
    preLoaders: [
      {
        test: /\.js/,
        loader: 'eslint'
      }
    ],
    loaders: [
      {
        test: /\.js/,
        exclude: /node_modules/,
        loaders: ['babel', 'baggage?[file].html=template&[file].scss'],
        include: __dirname + '/{{ project_name }}/assets'
      },
      {
        test: /\.scss/,
        loader: production ? ExtractPlugin.extract('style', 'css!postcss!sass?includePaths[]=' + path.resolve(__dirname, 'node_modules')) : 'style!css!postcss!sass?includePaths[]=' + path.resolve(__dirname, 'node_modules')
      },
      {
        test: /\.html/,
        loader: 'html'
      },
      {
        test: /\.(png|gif|jpe?g|svg)$/i,
        loader: 'url',
        query: {
          limit: 10000
        }
      }
    ]
  },

  plugins: plugins,
  postcss: function () {
    return [
      at2x,
      enter,
      fakeId,
      propertyLookup,
      pxToRem,
      willChange,

      // Autoprefixer always 2nd last as the other plugins might add code that
      // needs to be prefixed
      autoPrefixer,

      // Flexbugs always last as it might need to do something the browser
      // prefixed declarations
      flexbugFixes
    ];
  },

  resolve: {
    modulesDirectors: ['node_modules']
  }
};
