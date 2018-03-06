angular.module('zotnride.controllers', [])

.controller('AppCtrl', function($scope, $ionicModal, $rootScope, $timeout, $ionicHistory, $ionicPlatform, $ionicPopup, $http, $cordovaGeolocation, $cordovaDatePicker) {

  // With the new view caching in Ionic, Controllers are only called
  // when they are recreated or on app start, instead of every page change.
  // To listen for when this page is active (for example, to refresh data),
  // listen for the $ionicView.enter event:
  //$scope.$on('$ionicView.enter', function(e) {
  //});

  // Form data for the login modal
  $scope.loginData = {};

  $ionicModal.fromTemplateUrl('templates/login.html', {
    scope: $scope,
    animation: 'slide-in-up'
  }).then(function(modal) {
    $scope.loginModal = modal;
  });

  $scope.closeLogin = function() {
    $scope.loginModal.hide();
    if ($ionicHistory.currentView().title === 'Reservations')
      $ionicHistory.backView().go();
  };

  $scope.showLogin = function() {
    $scope.loginModal.show();
  };

  // Reserve Modal
  $ionicModal.fromTemplateUrl('templates/reserve.html', {
    scope: $scope,
    animation: 'slide-in-up'
  }).then(function(modal) {
    $scope.reserveModal = modal;
  });

  $scope.closeReserve = function() {
    $scope.reserveModal.hide();
  };

  $scope.showReserve = function() {
    if (window.localStorage.getItem('uid') === null || window.localStorage.getItem('uid') === '') {
      $scope.loginModal.show();
    } else
    $scope.reserveModal.show();
  };

  // Perform login
  $scope.doLogin = function() {
    $http({
      method: 'POST',
      url: API_URL + '/api/login',
      data: {
        email: $scope.loginData.email,
        password: $scope.loginData.password
      },
      headers: {'Content-Type': 'application/x-www-form-urlencoded'},
      transformRequest: function(obj) {
        var str = [];
        for(var p in obj)
        str.push(encodeURIComponent(p) + "=" + encodeURIComponent(obj[p]));
        return str.join("&");
      }
    }).then(function successCallback(response) {
      if (response.data === '') {
        $scope.showLoginFailedAlert = function() {
          var alertPopup = $ionicPopup.alert({
            title: 'Login Failed',
            template: 'Email/password is incorrect.'
          });
        };

        $scope.showLoginFailedAlert();
      } else {
        window.localStorage.setItem('uid', response.data.uid);
        window.localStorage.setItem('first_name', response.data.first_name);
        window.localStorage.setItem('last_name', response.data.last_name);
        $scope.loadReservations();
        $scope.loginModal.hide();
        if ($ionicHistory.currentView().title === 'Listing')
          $scope.showReserve();
      }
    }, function errorCallback(response) {
      console.log(JSON.stringify(response));
    });
  };

  $ionicPlatform.ready(function() {
    // Get device location
    $cordovaGeolocation.getCurrentPosition({
      enableHighAccuracy: false
    }).then(function(position) {
      $scope.lat = position.coords.latitude;
      $scope.lng = position.coords.longitude;
    }, function(err) {
      console.log(err);
    })

    // Datepicker
    $scope.setStartDate = function() {
      $cordovaDatePicker.show({
        date: $scope.startDateTime,
        mode: 'datetime',
        minDate: $scope.startDateTime,
        allowOldDates: false,
        minuteInterval: 30
      }).then(function(datetime) {
        $scope.startDateTime = datetime.toDateString() + ' ' + datetime.toLocaleTimeString();
        $scope.getStartDateTime = 'From: ' + $scope.startDateTime;
        endDateTime = new Date(new Date(new Date(new Date($scope.startDateTime).setHours(new Date($scope.startDateTime).getHours() + 1)).setMinutes(0)).setSeconds(0));
        $scope.endDateTime = endDateTime.toDateString() + ' ' + endDateTime.toLocaleTimeString();
        $scope.getEndDateTime = 'To: ' + $scope.endDateTime;
        searchListings();
      });
    }

    $scope.setEndDate = function() {
      $cordovaDatePicker.show({
        date: $scope.endDateTime,
        mode: 'datetime',
        minDate: $scope.startDateTime,
        allowOldDates: false,
        minuteInterval: 30
      }).then(function(datetime) {
        $scope.endDateTime = datetime.toDateString() + ' ' + datetime.toLocaleTimeString();
        $scope.getEndDateTime = 'To: ' + $scope.endDateTime;
        searchListings();
      });
    }
  });
})

.controller('ReservationsCtrl', function($scope, $stateParams, $http) {
  
})

.controller('ListingCtrl', function($scope, $stateParams, $rootScope, $http, $ionicModal) {

});