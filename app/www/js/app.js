angular.module('zotnride', ['ionic', 'zotnride.controllers', 'ngCordova', 'thatisuday.dropzone'])

.run(function($ionicPlatform, $ionicHistory) {
  $ionicPlatform.ready(function() {
    // Hide the accessory bar by default (remove this to show the accessory bar above the keyboard
    // for form inputs)
    if (window.cordova && window.cordova.plugins.Keyboard) {
      cordova.plugins.Keyboard.hideKeyboardAccessoryBar(true);
      cordova.plugins.Keyboard.disableScroll(true);

    }
    if (window.StatusBar) {
      // org.apache.cordova.statusbar required
      StatusBar.styleDefault();
    }
  });
})

.config(function($stateProvider, $urlRouterProvider) {
  $stateProvider

    .state('app', {
    url: '/app',
    abstract: true,
    templateUrl: 'templates/menu.html',
    controller: 'AppCtrl'
  })

  .state('app.main', {
    url: '/main',
    views: {
      'menuContent': {
        templateUrl: 'templates/main.html'
      }
    }
  })

  .state('app.listing', {
    url: '/listing/:listingId',
    views: {
      'menuContent': {
        templateUrl: 'templates/listing.html',
        controller: 'ListingCtrl'
      }
    }
  })

  .state('app.registration', {
    url: '/registration',
    views: {
      'menuContent': {
        templateUrl: 'templates/registration.html',
        controller: 'RegistrationCtrl'
      }
    }
  })

  .state('app.upload', {
    url: '/upload',
    views: {
      'menuContent': {
        templateUrl: 'templates/upload.html',
        controller: 'UploadCtrl'
      }
    }
  })

  .state('app.reservation', {
    url: '/reservations/:reservationId',
    views: {
      'menuContent': {
        templateUrl: 'templates/reservation.html',
        controller: 'ReservationsCtrl'
      }
    }
  })
  // if none of the above states are matched, use this as the fallback
  $urlRouterProvider.otherwise('/app/main');
});
