<template>
  <v-app>
    <ac-form-dialog v-model="expanded" ref="dialog"/>
    <div id="modal-target" />
  </v-app>
</template>

<script lang="ts">
import {Component, toNative} from 'vue-facing-decorator'
import AcFormDialog from '@/components/wrappers/AcFormDialog.vue'
import {ArtVue} from '@/lib/lib.ts'

@Component({
  components: {AcFormDialog},
})
class FormDialogContainer extends ArtVue {
  public expanded = false
}
export default toNative(FormDialogContainer)
</script>

<style scoped>

</style>
