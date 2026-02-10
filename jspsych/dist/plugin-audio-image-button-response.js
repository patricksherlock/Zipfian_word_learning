var jsPsychAudioImageButtonResponse = (function (jspsych) {
  'use strict';

  const info = {
      name: "audio-image-button-response",
      parameters: {
        /** Delay between image and audio */
          audio_delay: {
              type: jspsych.ParameterType.INT,
              pretty_name: "Audio delay",
              default: null,
          },
          change_audio_order: {
              type: jspsych.ParameterType.BOOL,
              pretty_name: "Change audio order",
              default: false,
          },
          inter_audio_gap: {
              type: jspsych.ParameterType.INT,
              pretty_name: "Inter audio gap",
              default: 3000,
          },
          image: {
              type: jspsych.ParameterType.HTML_STRING,
              pretty_name: "image",
              default: null,
          },
          /** The HTML string to be displayed */
          audio1: {
              type: jspsych.ParameterType.HTML_STRING,
              pretty_name: "Audio1",
              default: undefined,
          },
          /** The HTML string to be displayed */
          audio2: {
              type: jspsych.ParameterType.HTML_STRING,
              pretty_name: "Audio2",
              default: undefined,
          },
          /** Array containing the label(s) for the button(s). */
          choices: {
              type: jspsych.ParameterType.STRING,
              pretty_name: "Choices",
              default: undefined,
              array: true,
          },
          /** The HTML for creating button. Can create own style. Use the "%choice%" string to indicate where the label from the choices parameter should be inserted. */
          button_html: {
              type: jspsych.ParameterType.HTML_STRING,
              pretty_name: "Button HTML",
              default: '<button class="jspsych-btn">%choice%</button>',
              array: true,
          },
          /** Any content here will be displayed under the button(s). */
          prompt: {
              type: jspsych.ParameterType.HTML_STRING,
              pretty_name: "Prompt",
              default: null,
          },
          /** How long to show the stimulus. */
          stimulus_duration: {
              type: jspsych.ParameterType.INT,
              pretty_name: "Stimulus duration",
              default: null,
          },
          /** How long to show the trial. */
          trial_duration: {
              type: jspsych.ParameterType.INT,
              pretty_name: "Trial duration",
              default: null,
          },
          /** The vertical margin of the button. */
          margin_vertical: {
              type: jspsych.ParameterType.STRING,
              pretty_name: "Margin vertical",
              default: "0px",
          },
          /** The horizontal margin of the button. */
          margin_horizontal: {
              type: jspsych.ParameterType.STRING,
              pretty_name: "Margin horizontal",
              default: "8px",
          },
          /** If true, then trial will end when user responds. */
          response_ends_trial: {
              type: jspsych.ParameterType.BOOL,
              pretty_name: "Response ends trial",
              default: true,
          },
      },
  };
  /**
   * html-button-response
   * jsPsych plugin for displaying a stimulus and getting a button response
   * @author Josh de Leeuw
   * @see {@link https://www.jspsych.org/plugins/jspsych-html-button-response/ html-button-response plugin documentation on jspsych.org}
   */
  class HtmlButtonResponsePlugin {
      constructor(jsPsych) {
          this.jsPsych = jsPsych;
      }
      trial(display_element, trial) {

          // display stimulus
          // display image
          var html = '<div id="jspsych-html-button-response-stimulus">' + trial.image + "</div>";

          var audio_options = [trial.audio1, trial.audio2]
          if (trial.change_audio_order) {
            audio_options = [trial.audio2, trial.audio1]
          }
          //audio_options = jsPsych.randomization.repeat(audio_options, 1)
          //console.log(audio_options)

          // audio
          html += '<audio id="first_audio"> <source src="' + audio_options[0] + '" type="audio/mp3"> </audio>'
          html += '<audio id="second_audio"> <source src="' + audio_options[1] + '" type="audio/mp3"> </audio>'


          //display buttons
          var buttons = [];
          if (Array.isArray(trial.button_html)) {
              if (trial.button_html.length == trial.choices.length) {
                  buttons = trial.button_html;
              }
              else {
                  console.error("Error in html-button-response plugin. The length of the button_html array does not equal the length of the choices array");
              }
          }
          else {
              for (var i = 0; i < trial.choices.length; i++) {
                  buttons.push(trial.button_html);
              }
          }
          html += '<div id="jspsych-html-button-response-btngroup">';
          for (var i = 0; i < trial.choices.length; i++) {
              var str = buttons[i].replace(/%choice%/g, trial.choices[i]);
              html +=
                  '<div class="jspsych-html-button-response-button" style="display: inline-block; margin:' +
                      trial.margin_vertical +
                      " " +
                      trial.margin_horizontal +
                      '" id="jspsych-html-button-response-button-' +
                      i +
                      '" data-choice="' +
                      i +
                      '">' +
                      str +
                      "</div>";
          }
          html += "</div>";

          //show prompt if there is one
          if (trial.prompt !== null) {
              html += trial.prompt;
          }

          display_element.innerHTML = html;
          disable_buttons();

          // start time
          var start_time = performance.now();

          // play audio
          const first_audio = document.getElementById("first_audio");
          const second_audio = document.getElementById("second_audio");
          var prompt = document.getElementById("#prompt");


          setTimeout(function(){
            first_audio.play()

            first_audio.addEventListener('playing', function(){
              var btns = document.querySelectorAll(".jspsych-html-button-response-button button");
              btns[0].style.color = "black";
              btns[0].style.backgroundColor =  "#b0c4de";
            })

            second_audio.addEventListener('playing', function(){
              var btns = document.querySelectorAll(".jspsych-html-button-response-button button");
              btns[1].style.color = "black";
              btns[1].style.backgroundColor =  "#b0c4de";
            })

            first_audio.addEventListener('ended', function(){
              setTimeout(() => {second_audio.play();}, trial.inter_audio_gap);

              var btns = document.querySelectorAll(".jspsych-html-button-response-button button");
              btns[0].style.color = "black";
              btns[0].style.backgroundColor =  "white";

            })
            second_audio.addEventListener('ended', function(){
              var btns = document.querySelectorAll(".jspsych-html-button-response-button button");
              btns[1].style.color = "black";
              btns[1].style.backgroundColor =  "white";

              display_element.querySelector("#prompt").hidden = false;


              enable_buttons();

              // add event listeners to buttons
              for (var i = 0; i < trial.choices.length; i++) {
                  display_element
                      .querySelector("#jspsych-html-button-response-button-" + i)
                      .addEventListener("click", (e) => {
                      var btn_el = e.currentTarget;
                      var choice = btn_el.getAttribute("data-choice"); // don't use dataset for jsdom compatibility
                      after_response(choice);
                  });
              };
            })
          }, trial.audio_delay)

          // store response
          var response = {
              rt: null,
              button: null,
          };
          // function to end trial when it is time
          const end_trial = () => {
              // kill any remaining setTimeout handlers
              this.jsPsych.pluginAPI.clearAllTimeouts();
              // gather the data to store for the trial
              var trial_data = {
                  rt: response.rt,
                  image: trial.image,
                  response: response.button
              };
              // clear the display
              display_element.innerHTML = "";
              // move on to the next trial
              this.jsPsych.finishTrial(trial_data);
          };
          // function to handle responses by the subject
          function after_response(choice) {
              // measure rt
              var end_time = performance.now();
              var rt = Math.round(end_time - start_time);
              response.button = parseInt(choice);
              response.rt = rt;
              // after a valid response, the stimulus will have the CSS class 'responded'
              // which can be used to provide visual feedback that a response was recorded
              display_element.querySelector("#jspsych-html-button-response-stimulus").className +=
                  " responded";
              // disable all the buttons after a response
              var btns = document.querySelectorAll(".jspsych-html-button-response-button button");
              for (var i = 0; i < btns.length; i++) {
                  //btns[i].removeEventListener('click');
                  btns[i].setAttribute("disabled", "disabled");
              }
              if (trial.response_ends_trial) {
                  end_trial();
              }
          }
          // hide image if timing is set
          if (trial.stimulus_duration !== null) {
              this.jsPsych.pluginAPI.setTimeout(() => {
                  display_element.querySelector("#jspsych-html-button-response-stimulus").style.visibility = "hidden";
              }, trial.stimulus_duration);
          }
          // end trial if time limit is set
          if (trial.trial_duration !== null) {
              this.jsPsych.pluginAPI.setTimeout(end_trial, trial.trial_duration);
          }

          // button functions
          function disable_buttons() {
              var btns = document.querySelectorAll(".jspsych-html-button-response-button");
              for (var i = 0; i < btns.length; i++) {
                  var btn_el = btns[i].querySelector("button");
                  if (btn_el) {
                      btn_el.disabled = true;
                      btn_el.style.backgroundColor = "white";
                      btn_el.style.color = "black";
                  }
              }
          }
          function enable_buttons() {
              var btns = document.querySelectorAll(".jspsych-html-button-response-button");
              for (var i = 0; i < btns.length; i++) {
                  var btn_el = btns[i].querySelector("button");
                  if (btn_el) {
                      btn_el.disabled = false;
                  }
              }
          }
      }
      simulate(trial, simulation_mode, simulation_options, load_callback) {
          if (simulation_mode == "data-only") {
              load_callback();
              this.simulate_data_only(trial, simulation_options);
          }
          if (simulation_mode == "visual") {
              this.simulate_visual(trial, simulation_options, load_callback);
          }
      }
      create_simulation_data(trial, simulation_options) {
          const default_data = {
              stimulus: trial.stimulus,
              rt: this.jsPsych.randomization.sampleExGaussian(500, 50, 1 / 150, true),
              response: this.jsPsych.randomization.randomInt(0, trial.choices.length - 1),
          };
          const data = this.jsPsych.pluginAPI.mergeSimulationData(default_data, simulation_options);
          this.jsPsych.pluginAPI.ensureSimulationDataConsistency(trial, data);
          return data;
      }
      simulate_data_only(trial, simulation_options) {
          const data = this.create_simulation_data(trial, simulation_options);
          this.jsPsych.finishTrial(data);
      }
      simulate_visual(trial, simulation_options, load_callback) {
          const data = this.create_simulation_data(trial, simulation_options);
          const display_element = this.jsPsych.getDisplayElement();
          this.trial(display_element, trial);
          load_callback();
          if (data.rt !== null) {
              this.jsPsych.pluginAPI.clickTarget(display_element.querySelector(`div[data-choice="${data.response}"] button`), data.rt);
          }
      }
  }
  HtmlButtonResponsePlugin.info = info;

  return HtmlButtonResponsePlugin;

})(jsPsychModule);
