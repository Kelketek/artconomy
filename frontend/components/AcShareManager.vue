<template>
  <v-row no-gutters>
    <ac-related-manager
        :field-controller="newShare.fields.user_id" :list-controller="controller"
        item-key="user"
    >
      <template v-slot:preview="{item}">
        <v-col cols="4" sm="3" md="2" lg="1">
          <ac-avatar :user="item.x!.user" :removable="true" @remove="item.delete().catch(newShare.setErrors)"/>
        </v-col>
      </template>
      <template v-slot:default="{filter}">
        <v-col cols="12">
          <ac-bound-field
              label="Share with..."
              hint="Enter the username of another Artconomy user to share this with them."
              :field="newShare.fields.user_id" field-type="ac-user-select" :multiple="false" :filter="filter"/>
        </v-col>
      </template>
    </ac-related-manager>
  </v-row>
</template>

<script setup lang="ts">
import AcAvatar from './AcAvatar.vue'
import AcRelatedManager from './wrappers/AcRelatedManager.vue'
import AcBoundField from './fields/AcBoundField.ts'
import {genId} from '@/lib/lib.ts'
import {ListController} from '@/store/lists/controller.ts'
import {TerseUser} from '@/store/profiles/types/TerseUser.ts'
import {useForm} from '@/store/forms/hooks.ts'

const props = defineProps<{controller: ListController<TerseUser>}>()

const newShare = useForm('share_' + genId(), {
  endpoint: props.controller.endpoint,
  fields: {user_id: {value: null}},
})
</script>

<style scoped>

</style>
