API_URL = 'https://zot-n-ride.herokuapp.com';

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
  
  // var startDateTime = new Date(new Date(new Date(new Date().setHours(new Date().getHours() + 1)).setMinutes(0)).setSeconds(0));
  var startDateTime = moment();
  $scope.startDateTime = startDateTime.add(1, 'hours').minute(0);
  $scope.startDateTime = startDateTime.format('h:mm a');
  // var endDateTime = new Date(new Date(new Date(new Date().setHours(new Date().getHours() + 2)).setMinutes(0)).setSeconds(0));
  var endDateTime = moment().add(3, 'hours').minute(0);
  $scope.endDateTime = endDateTime.format('h:mm a');
  $scope.getStartDateTime = $scope.startDateTime;
  $scope.getEndDateTime =  $scope.endDateTime;

  $ionicModal.fromTemplateUrl('templates/login.html', {
    scope: $scope,
    animation: 'slide-in-up'
  }).then(function(modal) {
    $scope.loginModal = modal;
    $scope.loginModal.show();
  });

  $scope.closeLogin = function() {
    $scope.loginModal.hide();
    if ($ionicHistory.currentView().title === 'Registration')
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
        netID: $scope.loginData.email,
        password: $scope.loginData.password
      },
      headers: {'Content-Type': 'application/json'}
    }).then(function successCallback(response) {
      window.localStorage.setItem('netID', response.data.netID);
      $scope.loginModal.hide();
    }, function errorCallback(response) {
      $scope.showLoginFailedAlert = function() {
        var alertPopup = $ionicPopup.alert({
          title: 'Login Failed',
          template: 'Email/password is incorrect.'
        });
      };

      $scope.showLoginFailedAlert();
    });
  };

  $scope.setStartDate = function() { $cordovaDatePicker.show({
      date: $scope.startDateTime,
      mode: 'time',
      minDate: $scope.startDateTime,
      allowOldDates: false,
      minuteInterval: 30
    }).then(function(datetime) {
      $scope.startDateTime = datetime.toLocaleTimeString();
      $scope.getStartDateTime = 'From: ' + $scope.startDateTime;
      endDateTime = new Date(new Date(new Date(new Date($scope.startDateTime).setHours(new Date($scope.startDateTime).getHours() + 1)).setMinutes(0)).setSeconds(0));
      $scope.endDateTime = endDateTime.toLocaleTimeString();
      $scope.getEndDateTime = 'To: ' + $scope.endDateTime;
      searchListings();
    });
  }

  $scope.setEndDate = function() {
    $cordovaDatePicker.show({
      date: $scope.endDateTime,
      mode: 'time',
      minDate: $scope.startDateTime,
      allowOldDates: false,
      minuteInterval: 30
    }).then(function(datetime) {
      $scope.endDateTime = datetime.toLocaleTimeString();
      $scope.getEndDateTime = 'To: ' + $scope.endDateTime;
      searchListings();
    });
  }

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

.controller('RegistrationCtrl', function($scope, $stateParams, $http) {
  $scope.registrationData = {};

  $scope.registerAccount = function() {
  
  }
})

.controller('UploadCtrl', function($scope, $stateParams, $rootScope, $ionicHistory) {
  if (document.getElementById('DropzoneElementId')) {
    var myDropzone = new Dropzone("div#ical-dropzone", { url: "/file/post"});
  }

  $scope.goHome = function(){
    $ionicHistory.goBack(-2);
  }
  
  $scope.uploadSchedule = function() {
    $scope.goHome();
  }
})

.controller('ListingCtrl', function($scope, $stateParams, $rootScope, $http, $ionicModal) {

});