<template>
    <div class="patchbutton-wrapper" :class="classes">
      <v-btn :disabled="disabled" :color="trueVariant" v-if="value" @click="save" :class="classes">{{ falseText }}</v-btn>
      <v-btn :disabled="disabled" :class="classes" :color="falseVariant" v-else @click="save">{{ trueText }}</v-btn>
    </div>
</template>

<script>
  import {artCall} from '../lib'

  export default {
    name: 'ac-patchbutton',
    props: ['value', 'name', 'trueText', 'falseText', 'callback', 'classes', 'trueVariant', 'falseVariant', 'url', 'classes'],
    data: function () {
      return {
        disabled: false
      }
    },
    methods: {
      update () {
        this.$emit('input', !this.value)
      },
      save () {
        if (this.original === this.value) {
          this.editing = false
          return
        }
        let data = {}
        this.disabled = true
        data[this.name] = !this.value
        artCall(this.url, 'PATCH', data, this.postSave)
      },
      postSave () {
        this.update()
        if (this.callback) {
          this.callback()
        }
        this.disabled = false
      }
    }
  }
</script>

<style lang="scss">
  @import '../custom-bootstrap';
  .patchfield-preview {
    display: inline-block;
  }
  input.patch-input {
    padding: 0;
    margin: 0;
    background-color: $light-gray;
    border-color: $dark-purple;
    border-top: none;
    border-right: none;
    border-left: none;
    height: 1em;
    box-sizing: border-box;
  }
  textarea.patchfield-multiline-editor {
    width: 100%;
    height: 100%;
  }
  .patchfield-wrapper {
    display: inline-block;
  }
  .patchfield-multiline-wrapper {
    width: 100%;
    height: available;
  }
</style>
