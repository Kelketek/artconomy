<template>
  <div>
    <div v-if="editing" class="is-editing" @click="editing=false">Editing</div>
    <div v-else class="is-not-editing" @click="editing=true">Not Editing</div>
  </div>
</template>

<script lang="ts">
import Component, {mixins} from 'vue-class-component'
import Editable from '@/mixins/editable'
import {Prop} from 'vue-property-decorator'

  @Component
export default class EditableComponent extends mixins(Editable) {
    @Prop()
    public controls!: boolean
}
</script>
