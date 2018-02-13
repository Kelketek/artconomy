<template>
  <v-chip>
    <router-link v-if="tabName" :to="{name: 'Search', params: {tabName: tabName}, query: {q: [tag]}}">
      {{tag}}
    </router-link>
    <span v-else>
      {{tag}}
    </span>
    <span v-if="removable" @click="remove"><i class="fa fa-times"></i></span>
  </v-chip>
</template>

<style>
  .tag {
    display: inline-block;
    padding-left: .5rem;
    padding-right: .5rem;
    background-color: #dffffc;
    border-radius: .25rem;
    border: solid 1px black;
    margin-left: .1rem;
    margin-right: .1rem;
    margin-bottom: .1rem;
  }
</style>

<script>
  import { artCall } from '../lib'

  export default {
    name: 'ac-tag',
    props: {
      tag: {},
      removable: {
        type: Boolean,
        default: false
      },
      removeUrl: {},
      callback: {
        default: function () {}
      },
      tabName: {}
    },
    methods: {
      remove () {
        artCall(this.removeUrl, 'DELETE', {'tags': [this.tag]}, this.callback)
      }
    }
  }
</script>