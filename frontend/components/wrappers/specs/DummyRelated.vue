<template>
  <v-col>
    <ac-related-manager ref="manager" :list-controller="demoList" :field-controller="userForm.fields.user_id"
                        item-key="user">
      <template v-slot:preview="{item}">
        <v-col cols="4" sm="3" md="2" lg="1">
          <ac-avatar :user="item.x.user"
                     :removable="true" @remove="item.delete().catch(userForm.setErrors)"/>
        </v-col>
      </template>
      <template v-slot:default="{filter}">
        <ac-bound-field
            :field="userForm.fields.user_id" field-type="ac-user-select" :multiple="false" :filter="filter"/>
      </template>
    </ac-related-manager>
  </v-col>
</template>

<script setup lang="ts">
import AcRelatedManager from '../AcRelatedManager.vue'
import {User} from '@/store/profiles/types/User.ts'
import AcAvatar from '@/components/AcAvatar.vue'
import AcBoundField from '@/components/fields/AcBoundField.ts'
import {useList} from '@/store/lists/hooks.ts'
import {useForm} from '@/store/forms/hooks.ts'

const demoList = useList<User>('demoList', {endpoint: '/endpoint/', paginated: false})
const userForm = useForm('userForm', {endpoint: '/endpoint/', fields: {user_id: {value: null}}})
demoList.firstRun()
</script>
