<template>
    <div>
      <div v-if="toggle">
        <v-switch
            :label="value? falseText : trueText"
            v-model="model"
        />
      </div>
      <div v-else class="patchbutton-wrapper" :class="classes">
        <v-btn :disabled="disabled" :color="trueVariant" v-if="value" @click="save" :class="classes">{{ falseText }}</v-btn>
        <v-btn :disabled="disabled" :class="classes" :color="falseVariant" v-else @click="save">{{ trueText }}</v-btn>
      </div>
    </div>
</template>

<script>
  import {artCall} from '../lib'

  export default {
    name: 'ac-patchbutton',
    props: [
      'value',
      'name',
      'trueText',
      'falseText',
      'callback',
      'classes',
      'trueVariant',
      'falseVariant',
      'url',
      'classes',
      'toggle'
    ],
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
    },
    computed: {
      model: {
        get () {
          return this.value
        },
        set () {
          this.save()
        }
      }
    }
  }
</script>
