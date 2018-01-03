<template>
  <div class="patchdropdown-wrapper" :class="classes">
    <b-dropdown :disabled="disabled" :text="selected" class="m-md-2" v-if="editmode">
      <b-dropdown-item v-for="option in options" v-if="value + '' !== option.id" :key="option.id" @click="select(option.id)">
        {{ option.name }}
      </b-dropdown-item>
    </b-dropdown>
    <span v-else class="patchdropdown-preview" :class="classes">
      {{ selected }}
    </span>
  </div>
</template>

<script>
  import {artCall} from '../lib'

  export default {
    name: 'ac-patchdropdown',
    props: ['value', 'name', 'options', 'classes', 'callback', 'url', 'editmode'],
    data: function () {
      return {
        disabled: false,
        newValue: this.value
      }
    },
    computed: {
      selected () {
        let value = this.value + ''
        for (let option of this.options) {
          if (option['id'] === value) {
            return option['name']
          }
        }
      }
    },
    methods: {
      select (value) {
        this.newValue = value
        let data = {}
        this.disabled = true
        data[this.name] = value
        artCall(this.url, 'PATCH', data, this.postSave)
      },
      update () {
        this.$emit('input', this.newValue)
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
