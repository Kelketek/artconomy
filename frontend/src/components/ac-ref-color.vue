<template>
  <v-layout row class="pl-2 pr-2">
    <v-flex xs3>
      {{refColor.note}}
    </v-flex>
    <v-flex xs6 class="text-xs-center color-notation">{{refColor.color}}</v-flex>
    <v-flex xs2 v-if="editing" :style="'background-color: ' + refColor.color">&nbsp;</v-flex>
    <v-flex xs3 v-else :style="'background-color: ' + refColor.color">
      &nbsp;
    </v-flex>
    <v-flex xs1 v-if="editing" class="text-xs-center">
      <ac-action :success="callback" method="DELETE" :url="url" :button="false"><v-icon>delete</v-icon></ac-action>
    </v-flex>
  </v-layout>
</template>
<style>
  .ref-container{
    opacity: 0;
    padding: .1rem;
    display: inline-block;
  }
  .swatch {
    width: 100%;
    border: 2px solid #e0e0e0;
  }
  .swatch:hover .ref-container{
    background-color: #B8B8A9;
    color: #5f2480;
    opacity: 1;
  }
  .color-notation {
    font-family: monospace;
    text-transform: uppercase;
  }
</style>
<script>
  import AcAction from './ac-action'

  export default {
    components: {AcAction},
    props: ['refColor', 'editing', 'url', 'callback'],
    computed: {
      swatchStyle () {
        return (
          `background-color: ${this.refColor.color};` +
          `color: ${this.refColor.color};`
        )
      }
    }
  }
</script>