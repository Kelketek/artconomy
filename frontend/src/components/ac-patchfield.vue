<template>
    <div class="patchfield-wrapper" :class="classes()">
      <div v-if="editing"><input type="text" ref="field" v-focus="true" :value="value" @blur="save" @keyup.enter="save" @keyup.escape="reset" :disabled="disabled"></div>
      <div v-else-if="editmode" @click="editing=true"><div class="patchfield-preview" tabindex="0" @focus="editing=true" @input="update">{{ value }}</div><i class="fa fa-pencil" style="padding-left: 1em;"></i></div>
      <div v-else class="patchfield-normal">{{ value }}</div>
    </div>
</template>

<script>
  import { focus } from 'vue-focus'
  import {artCall} from '../lib'

  export default {
    name: 'ac-patchfield',
    directives: { focus: focus },
    props: ['value', 'editmode', 'name', 'styleclass', 'url', 'callback'],
    data: function () {
      return {
        editing: false,
        original: this.value,
        disabled: false
      }
    },
    methods: {
      update () {
        this.$emit('input', this.$refs.field.value)
      },
      reset () {
        this.$refs.field.value = this.original
        this.update()
        this.editing = false
      },
      save () {
        if (this.original === this.$refs.field.value) {
          this.editing = false
          return
        }
        this.update()
        let data = {}
        this.disabled = true
        data[this.name] = this.$refs.field.value
        artCall(this.url, 'PATCH', data, this.postSave)
      },
      postSave () {
        this.editing = false
        this.original = this.value
        this.disabled = false
        if (this.callback) {
          this.callback()
        }
      },
      classes () {
        if (this.styleclass) {
          let styles = {}
          styles[this.styleclass] = true
          return styles
        }
      }
    }
  }
</script>

<style>
  .patchfield-preview {
    display: inline-block;
    border-bottom: solid 1px black;
  }
  .patchfield-wrapper {
    display: inline-block;
  }
</style>
