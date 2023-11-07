<template>
  <div>
    <div v-if="editing" class="is-editing" @click="editing=false">Editing</div>
    <div v-else class="is-not-editing" @click="editing=true">Not Editing</div>
  </div>
</template>

<script lang="ts">
import {Component, mixins, Prop, toNative} from 'vue-facing-decorator'
import Editable from '@/mixins/editable'

@Component({})
class EditableComponent extends mixins(Editable) {
    @Prop()
    public controls!: boolean
}
export default toNative(EditableComponent)
</script>
